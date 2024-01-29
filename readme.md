# Telegram Bot - Chat ID ve API Token Ayarları

Bu proje, Telegram üzerinden mesaj gönderen bir Python komutu içermektedir. Bu komutu kullanabilmek için, Telegram BotFather ve @get_id_bot ile etkileşime geçerek aşağıdaki adımları takip etmeniz gerekmektedir.

## Chat ID Almak

1. Telegram uygulamasında, @get_id_bot ile sohbet başlatın veya "/start" komutunu kullanın.
2. @get_id_bot size bir yanıt gönderecek. Örneğin:

Hello YOUR_NAME
Your Chat ID = YOUR_CHAT_ID
User Name = YOUR_USERNAME

3. Yukarıdaki örnekte, `YOUR_CHAT_ID`'yi kopyalayın. Kopyaladiginiz CHAT_ID'yi `config.txt` dosyasinin icerisindeki `YOUR_CHAT_ID` yerine yazin.

## API Token (API Key) Almak

1. Telegram uygulamasında, @BotFather ile sohbet başlatın veya "/start" komutunu kullanın.
2. "/newbot" komutunu girin ve takip eden adımları izleyin.
3. BotFather size bir API Token sağlayacak. Örneğin:

Use this token to access the HTTP API: YOUR_API_TOKEN

4. Yukarıdaki örnekte, `YOUR_API_TOKEN`'ı kopyalayın. Kopyaladiginiz API_TOKEN'i `config.txt` dosyasinin icerisindeki `YOUR_API_KEY` yerine yazin.

## Botunuzun Ismini Aratarak Sohbet Başlatmak

1. Telegram uygulamasında, arama çubuğuna olusturdugunuz botun ismini yazarak arama yapın.
2. Botunuzu bulduktan sonra, bot ile bir sohbet başlatın veya "/start" komutunu kullanın.

## Projeyi Çalıştırmadan Önce Gereksinimleri İndirme
1. Terminal veya komut istemcisinde projenin ana dizinine gidin. (örneğin: `cd /path/to/your/project`)

2. Ardından, aşağıdaki komutu girerek gerekli Python kütüphanelerini yükleyin:
   pip install -r requirements.txt

## Projeyi Calistirmak
1. scraper.py calistirmaniz yeterli olucaktir.