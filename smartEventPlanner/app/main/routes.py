from flask import render_template, request, redirect, url_for
from app.models import Event
from app.main import bp


@bp.route('/')
def home():
    return redirect(url_for('main.index'))


@bp.route('/index', methods=['GET'])
def index():
    page = request.args.get('page', 1, type=int)
    category_filter = request.args.get('category', None)
    location_filter = request.args.get('location', None)

    query = Event.query.filter_by(is_approved=True)


    if category_filter:
        query = query.filter_by(category=category_filter)
    if location_filter:
        query = query.filter_by(location=location_filter)

    events = query.paginate(page=page, per_page=6, error_out=False)

    categories = ['Spor', 'Müzik', 'Sanat', 'Teknoloji', 'Eğitim', 'Kariyer', 'Yemek', 'Seyahat', 'Kitap', 'Film']
    locations = [
        'Adana', 'Adıyaman', 'Afyonkarahisar', 'Ağrı', 'Aksaray', 'Amasya',
        'Ankara', 'Antalya', 'Ardahan', 'Artvin', 'Aydın', 'Balıkesir', 'Bartın', 'Batman',
        'Bayburt', 'Bilecik', 'Bingöl', 'Bitlis', 'Bolu', 'Burdur', 'Bursa', 'Çanakkale',
        'Çankırı', 'Çorum', 'Denizli', 'Diyarbakır', 'Düzce', 'Edirne', 'Elazığ', 'Erzincan',
        'Erzurum', 'Eskişehir', 'Gaziantep', 'Giresun', 'Gümüşhane', 'Hakkari', 'Hatay',
        'Iğdır', 'Isparta', 'İstanbul', 'İzmir', 'Kahramanmaraş', 'Karabük', 'Karaman', 'Kars',
        'Kastamonu', 'Kayseri', 'Kırıkkale', 'Kırklareli', 'Kırşehir', 'Kilis', 'Kocaeli',
        'Konya', 'Kütahya', 'Malatya', 'Manisa', 'Mardin', 'Mersin', 'Muğla', 'Muş',
        'Nevşehir', 'Niğde', 'Ordu', 'Osmaniye', 'Rize', 'Sakarya', 'Samsun', 'Şanlıurfa',
        'Siirt', 'Sinop', 'Sivas', 'Şırnak', 'Tekirdağ', 'Tokat', 'Trabzon', 'Tunceli',
        'Uşak', 'Van', 'Yalova', 'Yozgat', 'Zonguldak'
    ]
    return render_template('index.html', events=events, categories=categories, locations=locations,
                           category_filter=category_filter, location_filter=location_filter)
