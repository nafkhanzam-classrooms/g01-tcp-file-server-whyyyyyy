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
- Pada program ini dimulai dari mengimport library yang dibutuhkan, menentuakan IP server, port, dan buffer size, menyimpan response server dan mentimpan data file yang didownload. Untuk mencegah race condition pada server-client, maka ditambagkan flag dan juga info pada saat event 'download' berjalan. 
- receiver() berguna sebagai thread yang akan terus berjalan untuk menerima data server, dan membuat semacam kondisi jika suatu event (koneksi putus, download, pesan, dll) terjadi. 
handle_download_stream() berguna untuk menuliskan file kedalam disk, dengan menggunakan info file untuk mengambil data dari queue  untuk dituliskan kedalam file. 
- upload() berguna untuk mengirimkan request ke server untuk mengupload file (apakah server siap) lalu mengirimkan file info yang perlukan. 
- download() berguna untuk hal yang sama dengan mengecek kesiapan dan mengambil file info dari server lalu menjalankan handle_download_steam untuk menulis. 
- list_files() berguna dengan meminta kepada server daftar file yang dimilikinya lalu menampilkan hasil yang didapat. 
- main sebagai program utama yang akan menjalankan koneksi pada server dan menjalankan thread receiver dan selalau kondisi masih menyala akan menghandle command yang sesuai. 

## server-poll.py
Merupaka program server yang akan menghandle request cleint dengan mekanisme poll yang akan mengecek banyak socket sekaligus tanpa bloking/menunggu satu client
- Hal yang pertama adalah mengimport library yang dibutuhkan dan membuat folder lokasi files untuk server
- Server (class) : semua logic server,  
  a. __init__ : inisialisasi awal program, membuat server jalan dilocalhost dan menyimpan konfigurasi sendiri.   Setelah itu menyimpan socket object berdasarkan FG dan alamat client.  
  b. broadcast : mengirim pesan ke semua client dengan cara looping fd (kecuali sender)  
  c. handle_request : menghandle semua request command dari client, memproses message, menyimpan alamat dan melihat command jenis apa yang ingin dijalankan. /list berarti mengambil semua file di folder server dan memberikan informasinya. /upload memberikan sinyal server siap, menyalakan blocking mode, dan menerima file dari client. /download memberikan sinyal, masuk mode blocking, lalu mengirimkan info file sesuai dengan yang dminta. 
- run : Membuat socket dan inisialisasi mode non-blocking, memonitor server socket dan menunggu event (client baru, handle command, dan shutdwon.   

## Screenshot Hasil
