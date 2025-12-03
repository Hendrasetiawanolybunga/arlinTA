from django.db import models
from django.contrib.auth.hashers import make_password
from django.db.models import Sum
from django.core.exceptions import ValidationError

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
        verbose_name_plural = 'Karyawan'  # Menghilangkan pluralisasi default

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
        verbose_name_plural = 'Produk'  # Menghilangkan pluralisasi default

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
        verbose_name_plural = 'Produksi'  # Menghilangkan pluralisasi default

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
        # Convert to int to ensure proper arithmetic
        stock_difference = int(self.jumlahHasil) - int(old_jumlah)
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
        verbose_name_plural = 'Detail Produksi'  # Menghilangkan pluralisasi default

    def clean(self):
        # Dapatkan jumlah lama jika sedang update
        old_jumlah = 0
        if self.pk:
            old_jumlah = DetailProduksi.objects.get(pk=self.pk).jumlahBahanTerpakai
            
        # Hitung stok yang akan digunakan/berubah
        # Convert to int to ensure proper arithmetic
        stok_yang_dibutuhkan = int(self.jumlahBahanTerpakai) - int(old_jumlah)
        
        # Cek hanya jika produk adalah Bahan Baku
        if self.idProduk.jenisProduk == 'Bahan Baku':
            if stok_yang_dibutuhkan > self.idProduk.stok:
                raise ValidationError(
                    f"Stok {self.idProduk.namaProduk} (Stok: {self.idProduk.stok}) tidak mencukupi untuk bahan terpakai {self.jumlahBahanTerpakai}."
                )
        super().clean()

    def save(self, *args, **kwargs):
        # Call clean method before saving
        self.clean()
        
        # Check if this is an update to an existing record
        is_update = self.pk is not None
        
        # Get the old quantity if this is an update
        old_jumlah = 0
        if is_update:
            old_instance = DetailProduksi.objects.get(pk=self.pk)
            old_jumlah = old_instance.jumlahBahanTerpakai
            
        super().save(*args, **kwargs)
        
        # Adjust stock based on the difference
        # Convert to int to ensure proper arithmetic
        stock_difference = int(self.jumlahBahanTerpakai) - int(old_jumlah)
        
        # Reduce stock of raw materials
        if self.idProduk.jenisProduk == 'Bahan Baku':
            self.idProduk.stok -= stock_difference
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
        verbose_name_plural = 'Pelanggan'  # Menghilangkan pluralisasi default

    def save(self, *args, **kwargs):
        # Hash password before saving if it's not already hashed
        if self.password and not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.namaPelanggan


class Pemesanan(models.Model):
    STATUS_CHOICES = [
        ('Diproses', 'Diproses'),
        ('Dikirim', 'Dikirim'),
        ('Selesai', 'Selesai'),
        ('Dibatalkan', 'Dibatalkan'),
    ]
    
    idPemesanan = models.AutoField(primary_key=True)
    tanggalPemesanan = models.DateField()
    totalPemesanan = models.IntegerField(default=0)
    keterangan = models.TextField(blank=True, null=True)
    idPelanggan = models.ForeignKey(Pelanggan, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Diproses')

    class Meta:
        db_table = 'pemesanan'

    class Admin:
        verbose_name = 'Pemesanan'
        verbose_name_plural = 'Pemesanan'  # Menghilangkan pluralisasi default

    def save(self, *args, **kwargs):
        # Removed aggregation logic - will be handled in admin
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pemesanan {self.idPelanggan}"


class DetailPemesanan(models.Model):
    idDetailPemesanan = models.AutoField(primary_key=True)
    idProduk = models.ForeignKey(Produk, on_delete=models.CASCADE)
    kuantiti = models.IntegerField()
    subTotal = models.IntegerField()
    idKoleksiPemesanan = models.ForeignKey(Pemesanan, on_delete=models.CASCADE)

    class Meta:
        db_table = 'detail_pemesanan'

    class Admin:
        verbose_name = 'Detail Pemesanan'
        verbose_name_plural = 'Detail Pemesanan'  # Menghilangkan pluralisasi default

    def save(self, *args, **kwargs):
        # Calculate subtotal automatically
        if not self.subTotal:
            self.subTotal = self.idProduk.harga * self.kuantiti
            
        # Check if this is an update to an existing record
        is_update = self.pk is not None
        
        # Get the old quantity if this is an update
        old_kuantiti = 0
        if is_update:
            old_instance = DetailPemesanan.objects.get(pk=self.pk)
            old_kuantiti = old_instance.kuantiti
            
        super().save(*args, **kwargs)
        
        # Note: Stock adjustment is now handled in PemesananAdmin based on status changes
        # No stock adjustment here anymore

    def __str__(self):
        return f"Detail Pemesanan {self.idKoleksiPemesanan}"