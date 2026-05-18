60 FPS Akıcılık: Kod yapısını tamamen elden geçirdim. Bellek sızıntılarına (memory leak) sebep olan ve her karede gereksiz tetiklenen döngüleri temizledim. Oyun en yoğun patlama anlarında bile donmadan, tamamen akıcı çalışıyor.

Hayalet Blok (Ghost Piece) Sistemi: Blokları sürüklerken tahtada nereye oturacaklarını gösteren yarı saydam bir gölge ekledim. Bu sayede hatalı yerleştirmelerin önüne geçiliyor ve çok daha rahat bir oynanış sunuyor.

Ekran Sarsıntısı (Screen Shake): Bloklar patladığında veya kombo yapıldığında, patlamanın büyüklüğüne göre ekran dinamik olarak titriyor. Oyuna harika bir vuruş ve tokluk hissi kattı.

Kombo ve Skor Çarpanları: Ardı ardına yapılan temizlemelerde 2x, 3x gibi kombo çarpanları devreye giriyor. Yüksek skorlarda ekranda parlayan özel animasyonlu yazılar yükseliyor.

Dinamik Parçacık Efektleri: Satır ve sütunlar silindiğinde çevreye dağılan, yer çekiminden etkilenen ve zamanla şeffaflaşarak kaybolan fizik parçacıkları kodladım.

Gelişmiş Tema Desteği: Oyun içinde anında değiştirilebilir 3 farklı renk paleti bulunuyor (Klasik Blue, Retro Pembe, Enerji Yeşil). Blok ve panel renkleri seçilen temaya göre otomatik şekilleniyor.

Grafik ve Yazı Önbellekleme: Skorlar ve yazılar her karede sıfırdan çizilmek yerine sadece değiştikçe bellekte güncelleniyor. Bu da işlemci ve ekran kartı yükünü neredeyse sıfıra indirdi.

Skor Hafızası ve Rekor Takibi: Hamle kalmadığında devreye giren şık bir bitiş ekranı var. En yüksek skoru hafızada tutuyor ve rekor kırıldığında özel bir kutlama efekti devreye giriyor.
