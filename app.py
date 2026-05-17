from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from agent import GorevYoneticisiAgent
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# .env dosyasını yükle
load_dotenv()

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

# Agent'ı oluştur
agent = GorevYoneticisiAgent()

def get_user_id():
    return request.headers.get('X-User-ID') or 'anonymous'

@app.route('/')
def index():
    """Ana sayfa"""
    return send_from_directory('frontend', 'index.html')

@app.route('/api/gorevler', methods=['GET'])
def gorevleri_getir():
    """Tüm görevleri getir"""
    try:
        gorevler = agent.tum_gorevleri_getir(get_user_id())
        return jsonify({
            "success": True,
            "gorevler": gorevler
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/gorevler', methods=['POST'])
def gorev_ekle():
    """Yeni görev ekle"""
    try:
        data = request.get_json()
        baslik = data.get('baslik')
        oncelik = data.get('oncelik', 'orta')
        tarih = data.get('tarih')
        
        if not baslik:
            return jsonify({
                "success": False,
                "error": "Görev başlığı gerekli!"
            }), 400
        
        gorev = agent.gorev_ekle(baslik, oncelik, tarih, get_user_id())
        
        return jsonify({
            "success": True,
            "gorev": gorev,
            "message": "Görev başarıyla eklendi!"
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/gorevler/<int:gorev_id>', methods=['PUT'])
def gorev_tamamla(gorev_id):
    """Görevi tamamla"""
    try:
        gorev = agent.gorev_tamamla(gorev_id, get_user_id())
        
        if gorev:
            return jsonify({
                "success": True,
                "gorev": gorev,
                "message": "Görev tamamlandı!"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Görev bulunamadı!"
            }), 404
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/gorevler/<int:gorev_id>', methods=['DELETE'])
def gorev_sil(gorev_id):
    """Görevi sil"""
    try:
        agent.gorev_sil(gorev_id, get_user_id())
        return jsonify({
            "success": True,
            "message": "Görev silindi!"
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/rapor', methods=['GET'])
def gunluk_rapor():
    """Günlük rapor getir"""
    try:
        rapor = agent.gunluk_rapor_olustur(get_user_id())
        return jsonify({
            "success": True,
            "rapor": rapor
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/oneriler', methods=['GET'])
def akilli_oneriler():
    """Akıllı önerileri getir"""
    try:
        lang = request.args.get("lang", "tr")
        oneriler = agent.akilli_oneri_olustur(lang=lang, user_id=get_user_id())

        return jsonify({
            "success": True,
            "oneriler": oneriler
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    
@app.route('/api/gorevler/<int:gorev_id>/calendar', methods=['GET'])
def gorev_takvim_dosyasi(gorev_id):
    """Görev için .ics takvim dosyası oluşturur"""
    try:
        gorevler = agent.tum_gorevleri_getir(get_user_id())
        gorev = next((g for g in gorevler if g["id"] == gorev_id), None)

        if not gorev:
            return jsonify({
                "success": False,
                "error": "Görev bulunamadı!"
            }), 404

        tarih = datetime.strptime(gorev["tarih"], "%Y-%m-%d")

        # Takvim etkinliği için varsayılan saat aralığı
        baslangic = tarih.replace(hour=9, minute=0, second=0)
        bitis = baslangic + timedelta(hours=1)

        uid = f"task-{gorev['id']}@gorev-yoneticisi-agent"
        olusturma_zamani = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

        dtstart = baslangic.strftime("%Y%m%dT%H%M%S")
        dtend = bitis.strftime("%Y%m%dT%H%M%S")

        baslik = gorev["baslik"].replace("\n", " ").replace(",", "\\,")
        oncelik = gorev.get("oncelik", "orta")

        aciklama = (
            f"Görev: {gorev['baslik']}\\n"
            f"Öncelik: {oncelik}\\n"
            f"Agent tarafından oluşturuldu."
        )

        ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Gorev Yoneticisi Agent//TR
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{olusturma_zamani}
DTSTART:{dtstart}
DTEND:{dtend}
SUMMARY:{baslik}
DESCRIPTION:{aciklama}
BEGIN:VALARM
TRIGGER:-PT1H
ACTION:DISPLAY
DESCRIPTION:Görev hatırlatması: {baslik}
END:VALARM
END:VEVENT
END:VCALENDAR
"""

        filename = f"gorev-{gorev_id}.ics"

        return Response(
            ics_content,
            mimetype="text/calendar",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "ok",
        "message": "Görev Yöneticisi Agent çalışıyor!"
    }), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
