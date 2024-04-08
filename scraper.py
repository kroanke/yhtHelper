# Author: kroanke, MTosun9

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from tkcalendar import Calendar
import tkinter as tk
from tkinter import ttk
from datetime import datetime, date, timedelta
import threading
import queue
import time
from ttkthemes import ThemedTk
import re
from tkinter import messagebox
from telegramMsg import send_to_telegram




child_elements = []
web_scraping_thread = None  # Declare web_scraping_thread as a global variable
timeAdjustment = False
def web_scraping_worker(city_from, city_to, departure_time, timeFrom, timeTo, time_adjustment_state, queue):
    if time_adjustment_state == 1:
        print("true")
        timeAdjustment = True
    else:
        print("false")
        timeAdjustment = False
    while True:
        
        try:
            print("web_scraping_worker STARTED...")
            options = webdriver.ChromeOptions()
            options.headless = True
            options.add_argument("--window-size=1920,1200")
            options.add_argument('user-agent=fake-useragent')
            options.add_argument("--disable-gpu")
            options.add_argument('--headless')
            driver = webdriver.Chrome(options=options)
            driver.wait = WebDriverWait(driver, 2)
            driver.get("https://ebilet.tcddtasimacilik.gov.tr/view/eybis/tnmGenel/tcddWebContent.jsf")

            city_from_input = driver.find_element(By.NAME, "nereden").send_keys(city_from)
            city_to_input = driver.find_element(By.NAME, "nereye").send_keys(city_to)
            departure_input = driver.find_element(By.NAME, "trCalGid_input")
            departure_input.clear()
            departure_input.send_keys(departure_time)

            departure_input.send_keys(Keys.TAB)

            submit_button = driver.find_element(By.NAME, "btnSeferSorgula").click()

            time.sleep(0.6)
            invalidRoute = driver.find_element(By.ID, "msg_container")
            child_elements = invalidRoute.find_elements(By.XPATH, "./*")
            time.sleep(2)
            if child_elements:
                switchButton()
                if table.get_children():
                    table.delete(*table.get_children())
                messagebox.showerror("Hata!", "İsteğinize Uygun Sefer Bulunmamaktadir!")
                print("No Route Found!")
                return
            else:
                table_rows = WebDriverWait(driver, 3).until(EC.presence_of_all_elements_located(
                    (By.XPATH, "//table[@role='grid']//tbody[@id='mainTabView:gidisSeferTablosu_data']//tr")))
                total_rows = len(table_rows)

                row_template = "//tr[@data-ri='{}']"

                all_rows_data = []
                for row_index in range(total_rows):
                    current_row_xpath = row_template.format(row_index)
                    try:

                        time_departure_element = driver.find_element(By.XPATH, current_row_xpath +
                                                                     "//td[1]//span[@class='seferSorguTableBuyuk']")
                        time_arrival_element = driver.find_element(By.XPATH, current_row_xpath +
                                                                   "//td[3]//span[@class='seferSorguTableBuyuk']")
                        seat_type_element = driver.find_element(By.XPATH, current_row_xpath +
                                                                "//td[5]//label[@class='ui-selectonemenu-label ui-inputfield ui-corner-all']")
                        price_element = driver.find_element(By.XPATH, current_row_xpath +
                                                            "//td[6]//label[@class='ui-outputlabel seferSorguTableBuyuk']")

                        time_departure_value = time_departure_element.text
                        time_arrival_value = time_arrival_element.text
                        seat_type_value = seat_type_element.text
                        price_value = price_element.text

                        seat_type_value = seat_type_value.replace(" ", "")
                        pattern = r'\((\d+)\)'
                        matches = re.findall(pattern, seat_type_value)


                        intDeparture = int(time_departure_value.replace(":", ""))
                        intArrival = int(time_arrival_value.replace(":",""))

                        if (timeFrom and not timeFrom.isspace()) and (timeTo  and not timeTo.isspace()):
                            
                            intTimeFrom = int(timeFrom.replace(":", ""))
                            intTimeTo = int(timeTo.replace(":", ""))
                        else:
                            print("b")
                        try:

                            if len(matches) > 0:
                                seat_type_value = matches[len(matches) - 1]
                                print(seat_type_value)
                                seat_type_value = int(seat_type_value)
                            else:
                                continue
                        except Exception as e:
                            seat_type_value = 0
                            print(f"INT CAST EXCEPTION {e}")
                            pass
                        if seat_type_value != 0:
                            if timeAdjustment:
                                print("a")
                                if intDeparture >= intTimeFrom and intArrival <= intTimeTo and intArrival > intTimeFrom:
                                    row_data = [time_departure_value, time_arrival_value, seat_type_value, price_value]
                                    all_rows_data.append(row_data)
                                else:
                                    print("Bilet var ama secilen saatler arasinda yok")

                            else:
                                row_data = [time_departure_value, time_arrival_value, seat_type_value, price_value]
                                all_rows_data.append(row_data)
                            
                            
                    except Exception as e:
                        print(f"Exception occurred! {e}")
                        print("Trying again..")
                        driver.quit()
                        web_scraping_worker(city_from, city_to, departure_time, timeFrom, timeTo,time_adjustment_state, queue)

                
                queue.put(all_rows_data)
                driver.quit()
                print("Search ENDED!")

                if len(all_rows_data) > 0:
                    messages = []
                    for bilet in all_rows_data:
                        a = str(departure_time) + " tarihinde " + city_from + " - " + city_to + " yönlü " + str(
                            bilet[0]) + " - " + str(bilet[1]) + " saatleri arasinda " + str(
                            bilet[2]) + " adet bilet bulunmustur."
                        messages.append(a)

                    # send_to_telegram(messages)
                    driver.quit()
                    return
                else:
                    print("NO DATA FOUND")
                    driver.quit()
                    time.sleep(3)
                    web_scraping_worker(city_from, city_to, departure_time,timeFrom, timeTo, time_adjustment_state, queue)


        except Exception as e:
            if child_elements:
                switchButton()
                if table.get_children():
                    table.delete(*table.get_children())
                messagebox.showerror("Hata!", "İsteğinize Uygun Sefer Bulunmamaktadır!")
                print("No Route Found!")
                return
            else:
                print(f"Error in web scraping worker: {e}")
                driver.quit()
                web_scraping_worker(city_from, city_to, departure_time, timeFrom, timeTo, time_adjustment_state, queue)


def submit():
    global web_scraping_thread
    if not city_from_var.get() or not city_to_var.get():
        messagebox.showerror("Error", "Lütfen gerekli alanlari doldurun.")
        return
    if table.get_children():
        table.delete(*table.get_children())
    switchButton()
    loading_row_id = table.insert('', 'end', values=("Loading...", "", "", ""))
    table.update()

    all_rows_data = []
    city_from = city_from_var.get()
    city_to = city_to_var.get()
    departure_time = cal.get_date()
    departure_time = datetime.strptime(departure_time, "%m/%d/%y").strftime("%d.%m.%Y")

    timeFrom =arrival_time_from_var.get()
    timeTo =arrival_time_to_var.get()
    print(timeFrom)
    print(timeTo)
    
    result_queue = queue.Queue()
    web_scraping_thread = threading.Thread(target=web_scraping_worker,
                                           args=(city_from, city_to, departure_time, timeFrom, timeTo,time_adjustment_var.get(), result_queue))
    web_scraping_thread.start()

    

    root.after(100, check_result_queue, web_scraping_thread, result_queue, loading_row_id)


        
def check_result_queue(web_scraping_thread, result_queue, loading_row_id):
    if web_scraping_thread.is_alive():
        root.after(100, check_result_queue, web_scraping_thread, result_queue, loading_row_id)
    elif not result_queue.empty():
        all_rows_data = result_queue.get()

        table.delete(loading_row_id)

        for index, row_data in enumerate(all_rows_data):
            table.insert('', index, values=row_data)

        switchButton()
def toggle_time_adjustment():
    if time_adjustment_var.get() == 1:
        arrival_time_from_dropdown.config(state="readonly", takefocus=True)
        arrival_time_to_dropdown.config(state="readonly", takefocus=True)
        arrival_time_from_dropdown['background'] = 'white'
        arrival_time_to_dropdown['background'] = 'white'
    else:
        arrival_time_from_dropdown.config(state="disabled", takefocus=False)
        arrival_time_to_dropdown.config(state="disabled", takefocus=False)
        arrival_time_from_dropdown['background'] = 'gray'
        arrival_time_to_dropdown['background'] = 'gray'


def update_arrival_time_to_options(event):
    selected_from_time = arrival_time_from_var.get()
    arrival_time_to_values = [f"{hour:02d}:00" for hour in range(int(selected_from_time[:2]) + 1, 24)]
    arrival_time_to_dropdown['values'] = arrival_time_to_values
def update_arrival_time_to_state(event):
    selected_from_time = arrival_time_from_var.get()
    current_to_time = arrival_time_to_var.get()
    if current_to_time and current_to_time < selected_from_time:
        arrival_time_to_var.set("")
    arrival_time_to_values = [f"{hour:02d}:00" for hour in range(int(selected_from_time[:2]) + 1, 24)]
    arrival_time_to_dropdown['values'] = arrival_time_to_values

def update_combobox_values(event, var, combobox, options):
    typed_text = var.get().replace('İ', 'i').lower()

    if not typed_text:
        combobox['values'] = options
    else:
        matching_options = sorted([option for option in options if typed_text in option.replace('İ', 'i').lower()],
                                  key=lambda x: x.lower().index(typed_text))
        combobox['values'] = matching_options
def handle_table_click(event):
    item = table.selection()[0]  # Get the selected item
    values = table.item(item, 'values')  # Get the values of the selected item
    print("Clicked on item:", values)

def switchButton():
    if submit_button["state"] == "normal":
        submit_button["state"] = "disabled"
        submit_button["text"] = "Searching.."
    else:
        submit_button["state"] = "normal"
        submit_button["text"] = "Search"

def show_warning_popup(event):
    print(event.widget.cget("state") == "disabled")
    print(event.widget.state())
    if "disabled" in event.widget.state():
        messagebox.showwarning("Warning", "Saat ayarini acmak icin sol alttaki 'Saat Ayari' kutucugunu isaretleyin")
        
with open('yhtHelper.txt', 'r') as file:
    yhtHelper = file.read()

    
print(yhtHelper)

root = ThemedTk(theme="arc")

root.title("Train Ticket Search")
cities = ["Adana", "Adana (Kiremithane)", "Adapazarı", "Adnanmenderes Havaalanı", "Afyon A.Çetinkaya", "Ahmetler",
          "Ahmetli", "Akgedik", "Akhisar", "Aksakal", "Akçadağ", "Akçamağara", "Akşehir", "Alayunt", "Alayunt Müselles",
          "Alaşehir", "Alifuatpaşa", "Aliköy", "Alp", "Alpu", "Alpullu", "Alöve", "Amasya", "Ankara Gar", "Araplı",
          "Argıthan", "Arifiye", "Artova", "Arıkören", "Asmakaya", "Atça", "Avşar", "Aydın", "Ayran", "Ayrancı",
          "Ayvacık", "Aşkale", "Bahçe", "Bahçeli (Km.755+290 S)", "Bahçeşehir", "Bahçıvanova", "Bakır", "Balıkesir",
          "Balıkesir (Gökköy)", "Balıköy", "Balışıh", "Banaz", "Bandırma Şehir", "Baraklı", "Baskil", "Batman",
          "Battalgazi", "Bağıştaş", "Bedirli", "Belemedik", "Bereket", "Beyhan", "Beylikköprü", "Beylikova", "Beyoğlu",
          "Beşiri", "Bilecik", "Bilecik YHT", "Bismil", "Biçer", "Bor", "Bostankaya", "Bozkanat", "Bozkurt", "Bozüyük",
          "Bozüyük YHT", "Boğazköprü", "Boğazköprü Müselles", "Boğazköy", "Buharkent", "Burdur", "Böğecik",
          "Büyükderbent YHT", "Büyükçobanlar", "Çadırkaya", "Çakmak", "Çalıköy", "Çamlık", "Çankırı", "Çardak",
          "Çatalca", "Çavundur", "Çavuşcugöl", "Çay", "Çağlar", "Çerikli", "Çerkezköy", "Çerkeş", "Çetinkaya",
          "Çiftehan", "Çizözü", "Çiğli", "Çobanhasan", "Çorlu", "Çukurbük", "Çukurhüseyin", "Çumra", "Çöltepe",
          "Çöğürler", "Caferli", "Ceyhan", "Cürek", "Dazkırı", "Demirdağ", "Demiriz", "Demirkapı", "Demirli",
          "Demiryurt", "Demirözü", "Denizli", "Derince YHT", "Değirmenözü", "Değirmisaz", "Diliskelesi YHT", "Dinar",
          "Divriği", "Diyarbakır", "Doğançay", "Doğanşehir", "Dumlupınar", "Durak", "Dursunbey", "Döğer", "ERYAMAN YHT",
          "Edirne", "Ekerek", "Ekinova", "Elazığ", "Elmadağ", "Emiralem", "Emirler", "Erbaş", "Ereğli", "Ergani",
          "Eriç", "Erzincan", "Erzurum", "Eskişehir", "Evciler", "Eşme", "Fevzipaşa", "Fırat", "Gazellidere",
          "Gaziantep", "Gaziemir", "Gazlıgöl", "Gebze", "Genç", "Germencik", "Germiyan", "Gezin", "Goncalı",
          "Goncalı Müselles", "Gökçedağ", "Gökçekısık", "Gölbaşı", "Gölcük", "Gömeç", "Göçentaşı", "Güllübağ", "Gümüş",
          "Gümüşgün", "Gündoğan", "Güneyköy", "Güneş", "Güzelbeyli", "Güzelyurt", "Hacıbayram", "Hacıkırı",
          "Hacırahmanlı", "Hanlı", "Hasankale", "Havza", "Hekimhan", "Hereke YHT", "Himmetdede", "Horasan", "Horozköy",
          "Horozluhan", "Horsunlu", "Huzurkent", "Hüyük", "Ildızım", "Ilgın", "Ilıca", "Irmak", "Isparta",
          "Ispartakule", "İhsaniye", "İliç", "İnay", "İncirlik", "İncirliova", "İsabeyli", "İshakçelebi", "İsmetpaşa",
          "İstanbul(Bakırköy)", "İstanbul(Bostancı)", "İstanbul(Halkalı)", "İstanbul(Pendik)", "İstanbul(Söğütlüçeşme)",
          "İzmir (Basmane)", "İzmit YHT", "Kabakça", "Kadılı", "Kadınhan", "Kaklık", "Kalecik", "Kalkancık", "Kalın",
          "Kandilli", "Kangal", "Kanlıca", "Kapaklı", "Kapıdere İstasyonu", "Kapıkule", "Karaali", "Karaağaçlı",
          "Karabük", "Karaisalıbucağı", "Karakuyu", "Karaköy", "Karalar", "Karaman", "Karaosman", "Karasenir", "Karasu",
          "Karaurgan", "Karaözü", "Kars", "Kavak", "Kavaklıdere", "Kayabaşı", "Kayabeyli", "Kayaş", "Kayseri",
          "Kayseri (İncesu)", "Kayışlar", "Kaşınhan", "Kelebek", "Kemah", "Kemaliye Çaltı", "Kemerhisar", "Keykubat",
          "Keçiborlu", "Kireç", "Km. 30+500", "Km. 37+362", "Km.102+600", "Km.139+500", "Km.156 Durak", "Km.171+000",
          "Km.176+000", "Km.186+000", "Km.282+200", "Km.286+500", "Konaklar", "Konya", "Konya (Selçuklu YHT)",
          "Kozdere", "Kumlu Sayding", "Kunduz", "Kurbağalı", "Kurfallı", "Kurt", "Kurtalan", "Kuyucak", "Kuşcenneti",
          "Kuşsarayı", "Köprüağzı", "Köprüköy", "Köprüören", "Köşk", "Kürk", "Kütahya", "Kılıçlar", "Kırkağaç",
          "Kırıkkale", "Kırıkkale YHT", "Kızoğlu", "Kızılca", "Kızılinler", "Ladik", "Lalahan", "Leylek", "Lüleburgaz",
          "Maden", "Malatya", "Mamure", "Manisa", "Mazlumlar", "Menderes", "Menemen", "Mercan", "Meydan", "Mezitler",
          "Meşelidüz", "Mithatpaşa", "Muradiye", "Muratlı", "Mustafayavuz", "Muş", "Narlı", "Nazilli", "Nizip", "Niğde",
          "Nohutova", "Nurdağ", "Nusrat", "Ortaklar", "Osmancık", "Osmaneli", "Osmaniye", "Oturak", "Ovasaray",
          "Oymapınar", "Palandöken", "Palu", "Pamukören", "Pancar", "Pazarcık", "Paşalı", "Pehlivanköy", "Piribeyler",
          "Polatlı", "Polatlı YHT", "Porsuk", "Pozantı", "Pınarbaşı", "Pınarlı", "Rahova", "Sabuncupınar", "Salat",
          "Salihli", "Sallar", "Samsun", "Sandal", "Sandıklı", "Sapanca", "Sarayköy", "Sarayönü", "Saruhanlı",
          "Sarıdemir", "Sarıkamış", "Sarıkent", "Sarımsaklı", "Sarıoğlan", "Savaştepe", "Sağlık", "Sekili", "Selçuk",
          "Sevindik", "Seyitler", "Sincan", "Sindirler", "Sinekli", "Sivas", "Sivas(Adatepe)", "Sivrice", "Soma",
          "Soğucak", "Subaşı", "Sudurağı", "Sultandağı", "Sultanhisar", "Suluova", "Susurluk", "Suveren", "Suçatı",
          "Söke", "Söğütlü Durak", "Süngütaşı", "Sünnetçiler", "Sütlaç", "Sıcaksu", "Şakirpaşa", "Şarkışla", "Şefaatli",
          "Şefkat", "Şehitlik", "Şerbettar", "Tanyeri", "Tatvan Gar", "Tavşanlı", "Tayyakadın", "Taşkent", "Tecer",
          "Tepeköy", "Tokat(Yeşilyurt)", "Topaç", "Topdağı", "Topulyurdu", "Torbalı", "Turgutlu", "Turhal", "Tuzhisar",
          "Tüney", "Türkoğlu", "Tınaztepe", "Ulam", "Uluköy", "Ulukışla", "Uluova", "Umurlu", "Urganlı", "Uyanık",
          "Uzunköprü", "Uşak", "Velimeşe", "Vezirhan", "Yahşihan", "Yahşiler", "Yakapınar", "Yarbaşı", "Yarımca YHT",
          "Yayla", "Yaylıca", "Yazlak", "Yazıhan", "Yağdonduran", "Yeni Karasar", "Yenice", "Yenice D", "Yenifakılı",
          "Yenikangal", "Yeniköy", "Yeniçubuk", "Yerköy", "Yeşilhisar", "Yolçatı", "Yozgat YHT", "Yunusemre", "Yurt",
          "Yıldırımkemal", "Yıldızeli", "Zile"]

style = ttk.Style()
style.configure("TLabel", padding=5, font=("Arial", 12))
style.configure("TButton", padding=10, font=("Arial", 12))
style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
style.configure("Treeview", font=("Arial", 12))

style.configure("TCombobox", fieldbackground="#FFECB3")
style.configure("TEntry", fieldbackground="#460680")

tk.Label(root, text="Nereden:").grid(row=0, column=0, padx=10, pady=10, sticky='e')
city_from_var = tk.StringVar()
city_from_dropdown = ttk.Combobox(root, textvariable=city_from_var, state="normal")
city_from_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky='w')
city_from_dropdown['values'] = cities
city_from_dropdown.bind("<KeyRelease>",
                        lambda event: update_combobox_values(event, city_from_var, city_from_dropdown, cities))

tk.Label(root, text="Nereye:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
city_to_var = tk.StringVar()
city_to_dropdown = ttk.Combobox(root, textvariable=city_to_var, state="normal")
city_to_dropdown.grid(row=1, column=1, padx=10, pady=10, sticky='w')
city_to_dropdown['values'] = cities
city_to_dropdown.bind("<KeyRelease>",
                      lambda event: update_combobox_values(event, city_to_var, city_to_dropdown, cities))


tk.Label(root, text="Arrival Time From:").grid(row=2, column=0, padx=10, pady=10, sticky='e')
arrival_time_from_var = tk.StringVar()
arrival_time_from_dropdown = ttk.Combobox(root, textvariable=arrival_time_from_var, state="readonly")
arrival_time_from_dropdown.grid(row=2, column=1, padx=10, pady=10, sticky='w')
arrival_time_from_dropdown['values'] = [f"{hour:02d}:00" for hour in range(24)]

tk.Label(root, text="Arrival Time To:").grid(row=3, column=0, padx=10, pady=10, sticky='e')
arrival_time_to_var = tk.StringVar()
arrival_time_to_dropdown = ttk.Combobox(root, textvariable=arrival_time_to_var, state="readonly")
arrival_time_to_dropdown.grid(row=3, column=1, padx=10, pady=10, sticky='w')
arrival_time_to_dropdown['values'] = [f"{hour:02d}:00" for hour in range(24)]

arrival_time_from_dropdown.bind("<<ComboboxSelected>>", update_arrival_time_to_options)
arrival_time_from_dropdown.bind("<<ComboboxSelected>>", update_arrival_time_to_state)

arrival_time_from_dropdown.bind("<Button-1>", show_warning_popup)
arrival_time_to_dropdown.bind("<Button-1>", show_warning_popup)

time_adjustment_var = tk.IntVar()
time_adjustment_checkbox = tk.Checkbutton(root, text="Saat Ayarı", variable=time_adjustment_var, command=toggle_time_adjustment)
time_adjustment_checkbox.grid(row=5, column=0, sticky='w')
toggle_time_adjustment()


current_date_time = datetime.now()
today = date.today()
maxDate = today + timedelta(days=30)
currentYear = current_date_time.year
currentMonth = current_date_time.month
currentDay = current_date_time.day
cal = Calendar(root, selectmode="day", year=currentYear, month=currentMonth, day=currentDay, mindate=today,
               maxdate=maxDate, background="#4d4d4d",
               selectbackground="#4d4d4d")
cal.grid(row=4, column=1, padx=10, pady=10, sticky='w')




submit_button = tk.Button(
    root,
    text="Search",
    command=submit,
    font=("Arial", 14, "bold"),
    bg="#4d4d4d",
    fg="white",
    padx=20,
    pady=10,
    relief="raised",
    activebackground="#3c3c3c",
)
submit_button.grid(row=5, column=1, pady=10)

table = ttk.Treeview(root, columns=('Time Departure', 'Time Arrival', 'Seat Type', 'Price'), show='headings')

table.heading('Time Departure', text='Çıkış Saati')
table.heading('Time Arrival', text='Varış Saati')
table.heading('Seat Type', text='Koltuk Sayısı')
table.heading('Price', text='Fiyat')
table.bind("<<TreeviewSelect>>", handle_table_click)
table.grid(row=6, column=0, columnspan=2, pady=10, sticky='nsew')

scrollbar = ttk.Scrollbar(root, orient="vertical", command=table.yview)
scrollbar.grid(row=7, column=2, sticky='ns')
table.configure(yscrollcommand=scrollbar.set)

for i in range(5):
    root.grid_rowconfigure(i, weight=1)
    root.grid_columnconfigure(i, weight=1)


#root.geometry("630x780")
#root.resizable(False, False)


root.mainloop()
