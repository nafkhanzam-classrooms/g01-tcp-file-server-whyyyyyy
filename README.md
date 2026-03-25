[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/mRmkZGKe)
# Network Programming - Assignment G01

## Anggota Kelompok
| Nama           | NRP        | Kelas     |
| ---            | ---        | ----------|
| Addien Zafriyan Al Akhsan      | 5025241058           | C           |
| Raden Kurniawan Agung Fitrianto               | 5025241104           | C          |
|                |            |           |

## Link Youtube (Unlisted)
Link ditaruh di bawah ini
```

```

## Penjelasan Program

### Client.py
Merupakan program yang berfungsi sebagai inisialisasi client sebagai pengguna yang akan berkomunikasi (broadcast), melihat akses (/list), mengakses file (/download), dan menambahkan files (/upload) untuk server yang akan dibuat.  
Pada program ini dimulai dari mengimport library yang dibutuhkan, menentuakan IP server, port, dan buffer size, menyimpan response server dan mentimpan data file yang didownload. Untuk mencegah race condition pada server-client, maka ditambagkan flag dan juga info pada saat event 'download' berjalan. 
receiver() berguna sebagai thread yang akan terus berjalan untuk menerima data server, dan membuat semacam kondisi jika suatu event (koneksi putus, download, pesan, dll) terjadi. 
handle_download_stream() berguna untuk menuliskan file kedalam disk, dengan menggunakan info file untuk mengambil data dari queue  untuk dituliskan kedalam file. 
upload() berguna untuk mengirimkan request ke server untuk mengupload file (apakah server siap) lalu mengirimkan file info yang perlukan. 
download() berguna untuk hal yang sama dengan mengecek kesiapan dan mengambil file info dari server lalu menjalankan handle_download_steam untuk menulis. 
list_files() berguna dengan meminta kepada server daftar file yang dimilikinya lalu menampilkan hasil yang didapat. 
main sebagai program utama yang akan menjalankan koneksi pada server dan menjalankan thread receiver dan selalau kondisi masih menyala akan menghandle command yang sesuai. 


## Screenshot Hasil
