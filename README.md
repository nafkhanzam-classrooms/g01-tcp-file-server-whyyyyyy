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
https://youtu.be/fmbER8cgrJk
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
Merupaka program server yang akan menghandle request cleint dengan menggunakan mekanisme poll, yaitu teknik I/O multiplexing yang memantau banyak socket menggunakan event berbasis file descriptor. Setiap socket (termasuk server dan client) didaftarkan ke dalam poller. Server kemudian akan terus melakukan pengecekan terhadap event yang terjadi, seperti adanya koneksi baru atau data yang masuk dari client.
Ketika event terjadi, poll akan mengembalikan daftar file descriptor yang aktif beserta jenis event-nya. Server kemudian memproses masing-masing event tersebut.
- Hal yang pertama adalah mengimport library yang dibutuhkan dan membuat folder lokasi files untuk server
- Server (class) : semua logic server,  
  a. __init__ : inisialisasi awal program, membuat server jalan dilocalhost dan menyimpan konfigurasi sendiri.   Setelah itu menyimpan socket object berdasarkan FG dan alamat client.  
  b. broadcast : mengirim pesan ke semua client dengan cara looping fd (kecuali sender)  
  c. handle_request : menghandle semua request command dari client, memproses message, menyimpan alamat dan melihat command jenis apa yang ingin dijalankan. /list berarti mengambil semua file di folder server dan memberikan informasinya. /upload memberikan sinyal server siap, menyalakan blocking mode, dan menerima file dari client. /download memberikan sinyal, masuk mode blocking, lalu mengirimkan info file sesuai dengan yang dminta. 
- run : Membuat socket dan inisialisasi mode non-blocking, memonitor server socket dan menunggu event (client baru, handle command, dan shutdwon.
  
## server-select.py
server-select.py merupakan program server yang menangani permintaan dari client menggunakan menggunakan mekanisme select, yaitu teknik I/O multiplexing yang memantau banyak socket menggunakan list descriptor dalam batas tertentu. Server akan menyimpan semua socket dalam sebuah list. Server kemudian menggunakan fungsi select untuk mengecek socket mana yang siap digunakan. Ketika select dipanggil, fungsi ini akan mengembalikan daftar socket yang aktif (readable). Server kemudian memproses setiap socket tersebut.

- Hal yang pertama adalah mengimport library yang dibutuhkan dan membuat folder lokasi files untuk server
- Server (class) : berisi seluruh logika server
  a. init : inisialisasi awal program, membuat socket server pada localhost, mengatur mode non-blocking, serta menyimpan daftar socket yang akan dimonitor (inputs) dan daftar client yang terhubung..
  b. broadcast : mengirim pesan ke semua client dengan cara looping fd (kecuali sender) dengan melakukan iterasi pada daftar client
  c. handle_request : menghandle semua request command dari client , memproses message, menyimpan alamat, mengganti mode blocking true dan melihat command jenis apa yang ingin dijalankan. /list berarti mengambil semua file di folder server dan - emberikan informasinya. /upload memberikan sinyal server siap, dan menerima file dari client. /download memberikan sinyal, lalu mengirimkan info file sesuai dengan yang dminta.
- run : menjalankan server dengan melakukan binding dan listening, lalu menggunakan select untuk memonitor banyak socket secara bersamaan, jika ada koneksi baru server akan menerima dan menambahkannya ke daftar monitoring, jika ada data masuk maka akan di handle_request, jika terjadi error, maka akan disconnect,

## server-sync.py
server-sync.py merupakan program server yang menghandle permintaan client menggunakan mekanisme synchronous (blocking), yaitu server hanya menangani satu client dalam satu waktu. Server akan menunggu/blocking hingga client selesai sebelum menerima client berikutnya. 
- Hal yang pertama adalah mengimport library yang dibutuhkan dan membuat folder lokasi files untuk server
- Server (class) : berisi seluruh logika server
  a. __init__ : inisialisasi awal program, menentukan host dan port server serta ukuran buffer yang digunakan untuk komunikasi data.  
  b. broadcast : mengirim pesan ke semua client yang terhubung (kecuali sender) dengan melakukan iterasi pada daftar client.
  c. handle_request : menghandle seluruh komunikasi dengan satu client secara terus-menerus (loop), menerima data, memproses message, dan menentukan command yang dijalankan. . /list berarti mengambil semua file di folder server dan memberikan informasinya . /upload memberikan sinyal server siap, dan menerima file dari client. /download memberikan sinyal, lalu mengirimkan info file sesuai dengan yang dminta.
  d. ketika client terputus, server akan menghapus client dari daftar dan menutup koneksi. 
- run : menjalankan server dengan membuat socket, melakukan binding dan listening. Server kemudian menerima koneksi client menggunakan accept(), dan langsung memproses client tersebut dengan handle_client. Karena menggunakan mekanisme blocking, server hanya akan melayani satu client sampai selesai sebelum menerima client berikutnya.

## server-thread.py
server-sync.py merupakan program server yang menghandle permintaan client menggunakan mekanisme multithreading , yaitu setiap client akan dilayani oleh thread berbeda.
- Hal yang pertama adalah mengimport library yang dibutuhkan dan membuat folder lokasi files untuk server
- ClientThread : berisi seluruh logika server
  a. __init__ : inisialisasi awal program, menentukan host dan port server serta ukuran buffer yang digunakan untuk komunikasi data.  
  b. broadcast : melakukan inisialisasi thread dengan menyimpan socket client, alamat client, serta ukuran buffer yang digunakan untuk komunikasi data.
  c. run : bagian utama, menambahkan client ke dalam list global dengan proteksi lock, melakukan loop untuk menerima dan memproses data,  dan menentukan command yang dijalankan. . /list berarti mengambil semua file di folder server dan memberikan informasinya . /upload memberikan sinyal server siap, dan menerima file dari client. /download memberikan sinyal, lalu mengirimkan info file sesuai dengan yang dminta.
  d. ketika client terputus, server akan menghapus client dari daftar dan menutup koneksi. 
- Server : menjalankan server dengan membuat socket, melakukan binding dan listenin. menerima client, membuat objek clientthread dan thread akan dijalankan secara pararel. 
## Screenshot Hasil
