from datetime import datetime
import json
import os
import random

# OpenAI entegrasyonu opsiyonel
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class GorevYoneticisiAgent:
    def __init__(self, dosya_adi="gorevler.json"):
        self.gorevler = []
        self.dosya_adi = dosya_adi
        self.gorevi_yukle()

    def gorevi_yukle(self):
        """Kaydedilmiş görevleri yükler."""
        try:
            with open(self.dosya_adi, "r", encoding="utf-8") as f:
                self.gorevler = json.load(f)
        except FileNotFoundError:
            self.gorevler = []
            self.gorevi_kaydet()
        except json.JSONDecodeError:
            self.gorevler = []
            self.gorevi_kaydet()

    def gorevi_kaydet(self):
        """Görevleri dosyaya kaydeder."""
        with open(self.dosya_adi, "w", encoding="utf-8") as f:
            json.dump(self.gorevler, f, ensure_ascii=False, indent=2)

    def gorev_ekle(self, baslik, oncelik="orta", tarih=None, user_id=None):
        """Yeni görev ekler."""
        if tarih is None:
            tarih = datetime.now().strftime("%Y-%m-%d")

        max_id = max([g.get("id", 0) for g in self.gorevler], default=0)

        gorev = {
            "id": max_id + 1,
            "user_id": user_id,
            "baslik": baslik,
            "oncelik": oncelik,
            "tarih": tarih,
            "tamamlandi": False,
            "olusturma": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        self.gorevler.append(gorev)
        self.gorevi_kaydet()
        return gorev

    def gorev_sil(self, gorev_id, user_id=None):
        """Görevi siler. Görev bulunduysa True, bulunamadıysa False döner."""
        onceki_uzunluk = len(self.gorevler)

        self.gorevler = [
            gorev for gorev in self.gorevler
            if not (gorev["id"] == gorev_id and (user_id is None or gorev.get("user_id") == user_id))
        ]

        self.gorevi_kaydet()
        return len(self.gorevler) < onceki_uzunluk

    def oncelikleri_analiz_et(self, user_id=None):
        """Görevleri önceliğe ve tarihe göre sıralar."""
        oncelik_sirasi = {
            "yüksek": 1,
            "orta": 2,
            "düşük": 3
        }

        gorevler = self.tum_gorevleri_getir(user_id)
        aktif_gorevler = [
            gorev for gorev in gorevler
            if not gorev["tamamlandi"]
        ]

        sirali_gorevler = sorted(
            aktif_gorevler,
            key=lambda gorev: (
                oncelik_sirasi.get(gorev["oncelik"], 4),
                gorev["tarih"]
            )
        )

        return sirali_gorevler

    def gun_farki_hesapla(self, tarih):
        """Görev tarihinin bugüne göre kaç gün önce/sonra olduğunu hesaplar."""
        bugun = datetime.now().date()
        gorev_tarihi = datetime.strptime(tarih, "%Y-%m-%d").date()
        return (gorev_tarihi - bugun).days

    def gunluk_rapor_olustur(self, user_id=None):
        """Günlük görev raporunu JSON formatında döner."""
        sirali = self.oncelikleri_analiz_et(user_id)
        gorevler = self.tum_gorevleri_getir(user_id)
        tamamlanan = [
            gorev for gorev in gorevler
            if gorev["tamamlandi"]
        ]

        return {
            "tarih": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "toplam_gorev": len(gorevler),
            "tamamlanan": len(tamamlanan),
            "bekleyen": len(sirali),
            "oncelikli_gorevler": sirali[:5]
        }

    def gorev_tamamla(self, gorev_id, user_id=None):
        """Görevi tamamlanmış olarak işaretler."""
        for gorev in self.gorevler:
            if gorev["id"] == gorev_id and (user_id is None or gorev.get("user_id") == user_id):
                gorev["tamamlandi"] = True
                gorev["tamamlanma"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                self.gorevi_kaydet()
                return gorev

        return None

    def akilli_oneri_olustur(self, lang="tr", user_id=None):
        """Agent'ın akıllı önerilerini JSON formatında döner."""
        lang = "en" if lang == "en" else "tr"
        sirali = self.oncelikleri_analiz_et(user_id)

        if not sirali:
            if lang == "en":
                dogal_oneri = random.choice([
                    "Great, you do not have any pending tasks right now. You can use this time to rest, plan ahead, or prepare your priorities for tomorrow.",
                    "All tasks seem to be completed. This is a good moment to take a short break and recharge your energy.",
                    "There are no pending tasks left. You can either enjoy a short pause or plan your next goals."
                ])
                mesaj = "🎉 Great! You have completed all your tasks!"
            else:
                dogal_oneri = random.choice([
                    "Harika, şu anda bekleyen görevin yok. Bu zamanı dinlenmek, plan yapmak ya da yarının önceliklerini düşünmek için kullanabilirsin.",
                    "Tüm görevlerini tamamlamış görünüyorsun. Bugün küçük bir mola vermek ve enerjini yenilemek iyi gelebilir.",
                    "Bekleyen iş kalmamış. Bu iyi bir fırsat; istersen yeni hedeflerini planlayabilir ya da kendine biraz zaman ayırabilirsin."
                ])
                mesaj = "🎉 Harika! Tüm görevleri tamamladınız!"

            return {
                "oneriler": [],
                "durum": "tamamlandi",
                "mesaj": mesaj,
                "dogal_oneri": dogal_oneri,
                "llm_oneri": None,
                "llm_kullanildi": False,
                "llm_aktif": self._llm_aktif_mi()
            }

        oneriler = []

        geciken = [
            gorev for gorev in sirali
            if self.gun_farki_hesapla(gorev["tarih"]) < 0
        ]

        if geciken:
            mesaj = (
                f"You have {len(geciken)} overdue task(s). It is better to handle them first."
                if lang == "en"
                else f"{len(geciken)} göreviniz gecikti! Önce onları halletmelisiniz."
            )
            oneriler.append({
                "tip": "gecikme",
                "ikon": "⚠️",
                "mesaj": mesaj,
                "gorevler": geciken[:3]
            })

        bugunun_gorevleri = [
            gorev for gorev in sirali
            if self.gun_farki_hesapla(gorev["tarih"]) == 0
        ]

        if bugunun_gorevleri:
            mesaj = (
                f"You have {len(bugunun_gorevleri)} task(s) due today."
                if lang == "en"
                else f"Bugün {len(bugunun_gorevleri)} göreviniz var."
            )
            oneriler.append({
                "tip": "bugun",
                "ikon": "📌",
                "mesaj": mesaj,
                "gorevler": bugunun_gorevleri
            })

        yuksek = [
            gorev for gorev in sirali
            if gorev["oncelik"] == "yüksek"
        ]

        if yuksek:
            if lang == "en":
                mesaj = f"You have {len(yuksek)} high-priority task(s)."
                oneri = f"You can start with '{yuksek[0]['baslik']}'."
            else:
                mesaj = f"{len(yuksek)} yüksek öncelikli göreviniz mevcut!"
                oneri = f"Öncelikle '{yuksek[0]['baslik']}' ile başlayabilirsiniz."

            oneriler.append({
                "tip": "oncelik",
                "ikon": "🔴",
                "mesaj": mesaj,
                "oneri": oneri,
                "gorevler": yuksek[:3]
            })

        yaklasan = [
            gorev for gorev in sirali
            if 0 < self.gun_farki_hesapla(gorev["tarih"]) <= 3
        ]

        if yaklasan:
            mesaj = (
                f"{len(yaklasan)} task(s) have deadlines within the next 3 days."
                if lang == "en"
                else f"{len(yaklasan)} görevinizin son tarihi yaklaşıyor (3 gün içinde)."
            )
            oneriler.append({
                "tip": "deadline",
                "ikon": "⏰",
                "mesaj": mesaj,
                "gorevler": yaklasan
            })

        dogal_oneri = self._kural_tabanli_dogal_oneri_olustur(sirali, oneriler, lang)

        llm_gerekiyor = self._llm_gerekli_mi(oneriler)

        llm_oneri = None
        if llm_gerekiyor:
            llm_oneri = self._llm_ile_oneri_olustur(sirali, lang, user_id)

        return {
            "oneriler": oneriler,
            "durum": "aktif",
            "toplam_oneri": len(oneriler),
            "dogal_oneri": dogal_oneri,
            "llm_oneri": llm_oneri,
            "llm_kullanildi": bool(llm_oneri),
            "llm_aktif": self._llm_aktif_mi()
        }

    def _kural_tabanli_dogal_oneri_olustur(self, sirali_gorevler, oneriler, lang="tr"):
        """
        OpenAI kullanmadan, görev analizine göre doğal dile yakın öneri üretir.
        Bu fonksiyon API/token harcamaz.
        """
        if not sirali_gorevler:
            if lang == "en":
                return "You do not have any pending tasks. You can take a short break or plan your next goals."
            return "Bekleyen görevin yok. Bugün biraz nefes alabilir ya da yeni hedeflerini planlayabilirsin."

        ilk_gorev = sirali_gorevler[0]
        ilk_gorev_baslik = ilk_gorev["baslik"]
        ilk_gorev_oncelik = ilk_gorev["oncelik"]
        ilk_gorev_gun_farki = self.gun_farki_hesapla(ilk_gorev["tarih"])

        tipler = {oneri.get("tip") for oneri in oneriler}

        geciken_sayisi = len([
            gorev for gorev in sirali_gorevler
            if self.gun_farki_hesapla(gorev["tarih"]) < 0
        ])

        bugun_sayisi = len([
            gorev for gorev in sirali_gorevler
            if self.gun_farki_hesapla(gorev["tarih"]) == 0
        ])

        yuksek_sayisi = len([
            gorev for gorev in sirali_gorevler
            if gorev["oncelik"] == "yüksek"
        ])

        yaklasan_sayisi = len([
            gorev for gorev in sirali_gorevler
            if 0 < self.gun_farki_hesapla(gorev["tarih"]) <= 3
        ])

        if lang == "en":
            girisler = [
                f"It would be best to focus on '{ilk_gorev_baslik}' first.",
                f"The most logical starting point right now seems to be '{ilk_gorev_baslik}'.",
                f"As a first step, I recommend focusing on '{ilk_gorev_baslik}'."
            ]

            if "gecikme" in tipler:
                devamlar = [
                    f"You have {geciken_sayisi} overdue task(s), so reducing that backlog first will help you move forward more comfortably.",
                    "Completing overdue tasks first can help you manage the rest of the day with more control.",
                    "Handling overdue work first will create more mental space for your next tasks."
                ]
            elif "deadline" in tipler:
                devamlar = [
                    f"{yaklasan_sayisi} task(s) have upcoming deadlines, so it is better to manage your time carefully.",
                    "Taking upcoming deadlines early can reduce last-minute stress.",
                    "Moving these tasks higher in your list will give you more flexibility later."
                ]
            elif "bugun" in tipler:
                devamlar = [
                    f"You have {bugun_sayisi} task(s) due today; moving in a short and clear order will help.",
                    "Breaking today’s tasks into smaller pieces can make them easier to complete.",
                    "Finishing today’s tasks first will help you close the day more cleanly."
                ]
            elif "oncelik" in tipler:
                devamlar = [
                    f"You have {yuksek_sayisi} high-priority task(s), so it makes sense to handle the critical ones first.",
                    "Completing high-priority tasks first will improve your productivity today.",
                    "Starting with high-priority work will make it easier to move on to lower-priority tasks later."
                ]
            else:
                devamlar = [
                    "Your tasks look generally under control, so moving step by step should be enough.",
                    "There is no urgent risk right now, but steady progress will help you keep a good pace.",
                    "Small and consistent steps should be enough for today."
                ]

            kapanislar = [
                "After that, you can continue with the remaining tasks based on priority.",
                "Then you can plan the lower-priority tasks according to the flow of your day.",
                "Once this is done, move on to the next important task on your list."
            ]

            if ilk_gorev_gun_farki < 0:
                zaman_notu = f"This task is {abs(ilk_gorev_gun_farki)} day(s) overdue."
            elif ilk_gorev_gun_farki == 0:
                zaman_notu = "This task is due today."
            elif ilk_gorev_gun_farki <= 3:
                zaman_notu = f"This task is due in {ilk_gorev_gun_farki} day(s)."
            else:
                priority_en = self._priority_to_en(ilk_gorev_oncelik)
                zaman_notu = f"This task is listed near the top because it has {priority_en} priority."

            return f"{random.choice(girisler)} {zaman_notu} {random.choice(devamlar)} {random.choice(kapanislar)}"

        girisler = [
            f"Bugün önceliğini '{ilk_gorev_baslik}' görevine vermen iyi olur.",
            f"Şu anda en mantıklı başlangıç noktası '{ilk_gorev_baslik}' gibi görünüyor.",
            f"İlk adım olarak '{ilk_gorev_baslik}' görevine odaklanmanı öneririm."
        ]

        if "gecikme" in tipler:
            devamlar = [
                f"Çünkü {geciken_sayisi} görevin gecikmiş durumda ve önce bu yükü azaltmak daha rahat ilerlemeni sağlar.",
                "Geciken görevleri kapatmak, günün geri kalanını daha kontrollü yönetmene yardımcı olur.",
                "Özellikle gecikmiş işleri önce tamamlamak, sonraki görevler için zihinsel alan açar."
            ]
        elif "deadline" in tipler:
            devamlar = [
                f"Çünkü {yaklasan_sayisi} görevin son tarihi yaklaşıyor; zamanı daha kontrollü kullanman iyi olur.",
                "Yaklaşan deadline'ları erkenden ele almak, son dakika stresini azaltır.",
                "Bu görevleri öne almak, ilerleyen saatlerde daha rahat hareket etmeni sağlar."
            ]
        elif "bugun" in tipler:
            devamlar = [
                f"Bugün tamamlanması gereken {bugun_sayisi} görevin var; kısa ve net bir sırayla ilerlemek iyi olur.",
                "Bugünkü görevleri küçük parçalara bölerek tamamlamak işini kolaylaştırabilir.",
                "Bugün yapılacakları önce bitirmek, günün sonunda daha temiz bir kapanış sağlar."
            ]
        elif "oncelik" in tipler:
            devamlar = [
                f"{yuksek_sayisi} yüksek öncelikli görevin olduğu için kritik işleri başa almak daha doğru olur.",
                "Yüksek öncelikli görevleri önce tamamlamak günün verimini artırır.",
                "Önceliği yüksek işlerden başlamak, daha sonra düşük öncelikli işlere daha rahat geçmeni sağlar."
            ]
        else:
            devamlar = [
                "Görevlerin genel olarak kontrol altında görünüyor; sırayla ilerlemek yeterli olacaktır.",
                "Şu an acil bir risk görünmüyor, ama düzenli ilerlemek iyi bir tempo sağlar.",
                "Bugün görevlerini küçük adımlarla ele alman yeterli görünüyor."
            ]

        kapanislar = [
            "Ardından kalan görevleri öncelik sırasına göre tamamlayabilirsin.",
            "Sonrasında daha düşük öncelikli görevleri günün akışına göre planlayabilirsin.",
            "Bunu bitirdikten sonra listedeki bir sonraki önemli göreve geçmen iyi olur."
        ]

        if ilk_gorev_gun_farki < 0:
            zaman_notu = f"Bu görev {abs(ilk_gorev_gun_farki)} gün gecikmiş görünüyor."
        elif ilk_gorev_gun_farki == 0:
            zaman_notu = "Bu görev bugün tamamlanmalı."
        elif ilk_gorev_gun_farki <= 3:
            zaman_notu = f"Bu görevin tamamlanmasına {ilk_gorev_gun_farki} gün kaldı."
        else:
            zaman_notu = f"Bu görev {ilk_gorev_oncelik} öncelikli olduğu için listenin üst sıralarında yer alıyor."

        return f"{random.choice(girisler)} {zaman_notu} {random.choice(devamlar)} {random.choice(kapanislar)}"

    def _priority_to_en(self, oncelik):
        if oncelik == "yüksek":
            return "high"
        if oncelik == "orta":
            return "medium"
        if oncelik == "düşük":
            return "low"
        return oncelik

    def _llm_aktif_mi(self):
        """
        OpenAI önerilerini environment variable ile açıp kapatır.

        .env içinde:
        USE_OPENAI_RECOMMENDATIONS=true  -> LLM önerileri aktif
        USE_OPENAI_RECOMMENDATIONS=false -> LLM önerileri kapalı
        """
        return os.getenv("USE_OPENAI_RECOMMENDATIONS", "false").lower() == "true"

    def _llm_gerekli_mi(self, oneriler):
        """
        LLM'i sadece gerçekten değer katacağı durumlarda çalıştırır.
        Böylece gereksiz OpenAI API ve token kullanımı önlenir.
        """
        if not self._llm_aktif_mi():
            return False

        api_key = os.getenv("OPENAI_API_KEY")

        if not OPENAI_AVAILABLE or not api_key:
            return False

        kritik_tipler = {
            "gecikme",
            "deadline"
        }

        for oneri in oneriler:
            if oneri.get("tip") in kritik_tipler:
                return True

        return False

    def _llm_ile_oneri_olustur(self, sirali_gorevler, lang="tr", user_id=None):
        """OpenAI API kullanarak doğal dil önerisi oluşturur."""
        api_key = os.getenv("OPENAI_API_KEY")

        if not OPENAI_AVAILABLE or not api_key:
            return None

        try:
            client = OpenAI(api_key=api_key)

            gorevler = self.tum_gorevleri_getir(user_id)
            toplam = len(gorevler)
            tamamlanan = len([
                gorev for gorev in gorevler
                if gorev["tamamlandi"]
            ])
            bekleyen = len(sirali_gorevler)

            gorev_listesi = []

            for gorev in sirali_gorevler[:5]:
                gun_farki = self.gun_farki_hesapla(gorev["tarih"])

                if lang == "en":
                    if gun_farki < 0:
                        durum = f"{abs(gun_farki)} day(s) overdue"
                    elif gun_farki == 0:
                        durum = "due today"
                    else:
                        durum = f"{gun_farki} day(s) left"
                    priority_text = self._priority_to_en(gorev["oncelik"])
                else:
                    if gun_farki < 0:
                        durum = f"{abs(gun_farki)} gün gecikti"
                    elif gun_farki == 0:
                        durum = "bugün bitiyor"
                    else:
                        durum = f"{gun_farki} gün kaldı"
                    priority_text = gorev["oncelik"]

                gorev_listesi.append(
                    f"- {gorev['baslik']} ({priority_text} priority, {durum})"
                )

            if lang == "en":
                prompt = f"""
You are a task management assistant.

Analyze the user's task status and write a short, motivating, friendly recommendation.

Status:
- Total tasks: {toplam}
- Completed: {tamamlanan}
- Pending: {bekleyen}

Priority tasks:
{chr(10).join(gorev_listesi)}

Rules:
- Write in English.
- Keep it within 2-3 sentences.
- Mention the most critical task first.
- If there is an overdue task, warn clearly but kindly.
- If a deadline is approaching, emphasize timing.
- Give realistic and actionable advice.
- Do not use Markdown.

Recommendation:
"""
                system_content = "You are a helpful, clear, and motivating task management assistant."
            else:
                prompt = f"""
Sen bir görev yönetimi asistanısın.

Kullanıcının görev durumunu analiz edip kısa, motive edici ve samimi bir öneri yaz.

Durum:
- Toplam görev: {toplam}
- Tamamlanan: {tamamlanan}
- Bekleyen: {bekleyen}

Öncelikli görevler:
{chr(10).join(gorev_listesi)}

Kurallar:
- Türkçe yaz.
- 2-3 cümleyi geçme.
- Önce en kritik görevi söyle.
- Gecikmiş görev varsa nazik ama net uyar.
- Deadline yaklaşmışsa zamanı vurgula.
- Gerçekçi ve yapılabilir öneri ver.
- Markdown kullanma.

Öneri:
"""
                system_content = "Sen yardımcı, net ve motive edici bir görev yönetimi asistanısın."

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": system_content
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=150,
                temperature=0.7
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"LLM öneri hatası: {e}")
            return None

    def tum_gorevleri_getir(self, user_id=None):
        """Kullanıcıya ait görevleri döner."""
        if user_id:
            return [g for g in self.gorevler if g.get("user_id") == user_id]
        return self.gorevler