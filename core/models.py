from django.db import models
from django.contrib.auth.hashers import make_password

# Create your models here.

class Karyawan(models.Model):
    idKaryawan = models.AutoField(primary_key=True)
    nama = models.CharField(max_length=255)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)

    class Meta:
        db_table = 'karyawan'

    class Admin:
        verbose_name = 'Karyawan'
        verbose_name_plural = 'Karyawan'

    def save(self, *args, **kwargs):
        # Hash password before saving if it's not already hashed
        if self.password and not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.nama


class Produk(models.Model):
    idProduk = models.AutoField(primary_key=True)
    namaProduk = models.CharField(max_length=50)
    jenisProduk = models.CharField(max_length=50, choices=[('Bahan Baku', 'Bahan Baku'), ('Produk Jadi', 'Produk Jadi')])
    harga = models.IntegerField()
    stok = models.IntegerField()
    satuan = models.CharField(max_length=20)

    class Meta:
        db_table = 'produk'

    class Admin:
        verbose_name = 'Produk'
        verbose_name_plural = 'Produk'

    def __str__(self):
        return self.namaProduk


class Produksi(models.Model):
    idProduksi = models.AutoField(primary_key=True)
    tanggalProduksi = models.DateField()
    jenisHasil = models.CharField(max_length=50, choices=[('Tahu', 'Tahu'), ('Tempe', 'Tempe')])
    jumlahHasil = models.IntegerField()
    satuanHasil = models.CharField(max_length=20)
    keterangan = models.TextField(blank=True, null=True)
    idKaryawan = models.ForeignKey(Karyawan, on_delete=models.CASCADE)

    class Meta:
        db_table = 'produksi'

    class Admin:
        verbose_name = 'Produksi'
        verbose_name_plural = 'Produksi'

    def save(self, *args, **kwargs):
        # Check if this is an update to an existing record
        is_update = self.pk is not None
        
        # Get the old quantity if this is an update
        old_jumlah = 0
        if is_update:
            old_instance = Produksi.objects.get(pk=self.pk)
            old_jumlah = old_instance.jumlahHasil
            
        super().save(*args, **kwargs)
        
        # Update product stock after saving
        if self.jenisHasil == 'Tahu':
            produk, created = Produk.objects.get_or_create(
                namaProduk='Tahu',
                defaults={
                    'jenisProduk': 'Produk Jadi',
                    'harga': 2000,  # Default price
                    'stok': 0,
                    'satuan': 'buah'
                }
            )
        elif self.jenisHasil == 'Tempe':
            produk, created = Produk.objects.get_or_create(
                namaProduk='Tempe',
                defaults={
                    'jenisProduk': 'Produk Jadi',
                    'harga': 2500,  # Default price
                    'stok': 0,
                    'satuan': 'buah'
                }
            )
            
        # Adjust stock based on the difference
        if is_update:
            stock_difference = self.jumlahHasil - old_jumlah
        else:
            stock_difference = self.jumlahHasil
            
        produk.stok += stock_difference
        produk.save()

    def __str__(self):
        return f"Produksi {self.jenisHasil} oleh {self.idKaryawan}"


class DetailProduksi(models.Model):
    idDetail = models.AutoField(primary_key=True)
    idProduk = models.ForeignKey(Produk, on_delete=models.CASCADE)
    jumlahBahanTerpakai = models.IntegerField()
    idProduksi = models.ForeignKey(Produksi, on_delete=models.CASCADE)

    class Meta:
        db_table = 'detail_produksi'

    class Admin:
        verbose_name = 'Detail Produksi'
        verbose_name_plural = 'Detail Produksi'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Reduce stock of raw materials
        if self.idProduk.jenisProduk == 'Bahan Baku':
            self.idProduk.stok -= self.jumlahBahanTerpakai
            self.idProduk.save()

    def __str__(self):
        return f"Detail Produksi {self.idProduksi}"


class Pelanggan(models.Model):
    idPelanggan = models.AutoField(primary_key=True)
    namaPelanggan = models.CharField(max_length=50)
    alamat = models.TextField()
    noTelp = models.CharField(max_length=15)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)

    class Meta:
        db_table = 'pelanggan'

    class Admin:
        verbose_name = 'Pelanggan'
        verbose_name_plural = 'Pelanggan'

    def save(self, *args, **kwargs):
        # Hash password before saving if it's not already hashed
        if self.password and not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.namaPelanggan


class Pembelian(models.Model):
    idPembelian = models.AutoField(primary_key=True)
    tanggalPembelian = models.DateField()
    totalPembelian = models.IntegerField(default=0)
    keterangan = models.TextField(blank=True, null=True)
    idPelanggan = models.ForeignKey(Pelanggan, on_delete=models.CASCADE)

    class Meta:
        db_table = 'pembelian'

    class Admin:
        verbose_name = 'Pembelian'
        verbose_name_plural = 'Pembelian'

    def save(self, *args, **kwargs):
        # Calculate total from details if not provided
        if not self.totalPembelian:
            total = self.detailpembelian_set.aggregate(
                total=Sum('subTotal')
            )['total'] or 0
            self.totalPembelian = total
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pembelian {self.idPelanggan}"


class DetailPembelian(models.Model):
    idDetailPembelian = models.AutoField(primary_key=True)
    idProduk = models.ForeignKey(Produk, on_delete=models.CASCADE)
    kuantiti = models.IntegerField()
    subTotal = models.IntegerField()
    idPembelian = models.ForeignKey(Pembelian, on_delete=models.CASCADE)

    class Meta:
        db_table = 'detail_pembelian'

    class Admin:
        verbose_name = 'Detail Pembelian'
        verbose_name_plural = 'Detail Pembelian'

    def save(self, *args, **kwargs):
        # Calculate subtotal automatically
        if not self.subTotal:
            self.subTotal = self.idProduk.harga * self.kuantiti
        super().save(*args, **kwargs)
        
        # Increase stock when purchasing raw materials
        if self.idProduk.jenisProduk == 'Bahan Baku':
            self.idProduk.stok += self.kuantiti
            self.idProduk.save()

    def __str__(self):
        return f"Detail Pembelian {self.idPembelian}"


class Penjualan(models.Model):
    idPenjualan = models.AutoField(primary_key=True)
    tanggalPenjualan = models.DateField()
    totalPenjualan = models.IntegerField(default=0)
    keterangan = models.TextField(blank=True, null=True)
    idKaryawan = models.ForeignKey(Karyawan, on_delete=models.CASCADE)
    idPelanggan = models.ForeignKey(Pelanggan, on_delete=models.CASCADE)

    class Meta:
        db_table = 'penjualan'

    class Admin:
        verbose_name = 'Penjualan'
        verbose_name_plural = 'Penjualan'

    def save(self, *args, **kwargs):
        # Calculate total from details if not provided
        if not self.totalPenjualan:
            total = self.detailpenjualan_set.aggregate(
                total=Sum('subTotal')
            )['total'] or 0
            self.totalPenjualan = total
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Penjualan {self.idPelanggan}"


class DetailPenjualan(models.Model):
    idDetailPenjualan = models.AutoField(primary_key=True)
    idPenjualan = models.ForeignKey(Penjualan, on_delete=models.CASCADE)
    kuantiti = models.IntegerField()
    subTotal = models.IntegerField()
    idProduk = models.ForeignKey(Produk, on_delete=models.CASCADE)

    class Meta:
        db_table = 'detail_penjualan'

    class Admin:
        verbose_name = 'Detail Penjualan'
        verbose_name_plural = 'Detail Penjualan'

    def save(self, *args, **kwargs):
        # Calculate subtotal automatically
        if not self.subTotal:
            self.subTotal = self.idProduk.harga * self.kuantiti
        super().save(*args, **kwargs)
        
        # Reduce stock when selling products
        if self.idProduk.jenisProduk == 'Produk Jadi':
            self.idProduk.stok -= self.kuantiti
            self.idProduk.save()

    def __str__(self):
        return f"Detail Penjualan {self.idPenjualan}"