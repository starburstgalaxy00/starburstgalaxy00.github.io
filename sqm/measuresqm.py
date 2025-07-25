import socket
import time
import csv
from astral.sun import sun
from astral import LocationInfo
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# 로그 기록하기
def log(message):
    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("SQMlog.txt","a",encoding="utf-8") as f:
        f.write(f"{timestamp} | {message}\n")

# 일몰, 일출 시간 불러오기
def nighttime():
    city=LocationInfo("Daejeon","South Korea", "Asia/Seoul", latitude=36.3667, longitude=127.3556)
    now=datetime.now(ZoneInfo(city.timezone))

    sun_today=sun(city.observer,date=now.date(),tzinfo=city.timezone)
    sun_tomorrow=sun(city.observer,date=now.date()+timedelta(days=1),tzinfo=city.timezone)

    sunset=sun_today["sunset"]
    sunrise=sun_tomorrow["sunrise"]

    return now, sunset, sunrise

# 데이터 평균값값 저장하기
def average(avg):
    today = datetime.now().strftime("%Y-%m-%d")
    with open("sqmavg.csv","a",newline="",encoding="utf-8") as f:
        writer=csv.writer(f)
        writer.writerow([today,avg])

# 데이터 일일값 저장하기
def daily(brightness_values, temperature_values, photon_values, timestamps, sunset):
    sunset_date = sunset.date().strftime("%Y-%m-%d")
    filename=f"{sunset_date}_sqm.csv"

    with open(filename,"w",newline="",encoding="utf-8") as f:
        writer=csv.writer(f)
        writer.writerow(["timestamp","brightness(m)","temperature(C)","photon(Hz)"])
        for ts, bri, temp, pho in zip(timestamps, brightness_values, temperature_values, photon_values):
            writer.writerow([ts,bri, temp, pho])

# 데이터 측정하기
def measurement(IP,PORT,timeinterval,sunset,now,sunrise):
    timeduration=sunrise-now
    # n=10
    n=int(timeduration.total_seconds()//timeinterval)
    success_count=0
    brightness_values=[]
    temperature_values=[]
    photon_values=[]
    timestamps=[]
    
    for i in range(n):
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
                s.settimeout(5)    
                try:
                    s.connect((IP,PORT))
                    # print("connection success")
                    # log("connection success")
                except Exception as e:
                    log(f"ERROR: Connection failed - {e}")
                    continue
                s.sendall(b'rx\r\n')
                data=s.recv(1024)
                if data:
                    decoded=data.decode(errors="ignore").strip()
                    parts=decoded.split(",")
                    print(f"{timestamp} | [{i+1:04d}] {decoded}")
                    success_count+=1
                    if len(parts) >=6:
                        brightness_str=parts[1].strip().replace("m","")
                        temperature_str=parts[5].strip().replace("C","")
                        photon_str=parts[2].strip().replace("Hz","")
                        try:
                            brightness=float(brightness_str)
                            temperature=float(temperature_str)
                            photon=float(photon_str)
                            brightness_values.append(brightness)
                            temperature_values.append(temperature)
                            photon_values.append(photon)
                            timestamps.append(timestamp)
                        except ValueError:
                            log(f"WARNING: Invalid brightness value at iteration {i+1}")
                else:
                    msg=f"No data at iteration {i+1}"
                    print(f"WARNING: {msg}")
                    log(f"WARNING: {msg}")
        except socket.timeout:
            msg=f"Timeout at iteration {i+1}"
            print(f"ERROR: {msg}")
            log(f"ERROR: {msg}")
        except Exception as e:
            log(f"ERROR: Unexpected error at iteration {i+1} - {e}")
            
        time.sleep(timeinterval)
    
    log(f"measurement completed({success_count}/{n})")
    print(f"measurement completed({success_count}/{n})")

    if brightness_values:
        avg_brightness=sum(brightness_values)/len(brightness_values)
        average(avg_brightness)
        daily(brightness_values,temperature_values,photon_values,timestamps,sunset)
        print(f"Average brightness saved: {avg_brightness}")
        log(f"average brightness saved: {avg_brightness}")
        print(f"Daily data saved")
        log(f"Daily data saved {i+1}")
    else:
        log("No valid brightness data collected.")

measured_today=False

IP=''
PORT=10001
timeinterval=60

while True:
    now, sunset, sunrise = nighttime()

    if sunset <= now < sunrise:
        if not measured_today:
            try:
                log(f"measurement started")
                print(f"measurement started")
                measurement(IP,PORT,timeinterval,sunset,now,sunrise)
                measured_today=True
            except Exception as e:
                log(f"Critical measurement error: {e}")
                measured_today=False
        time.sleep(1)
    else:
        measured_today=False
        sleep_seconds=max((sunset-now).total_seconds()-60, 300)
        log(f"Daytime detected. Sleeping for {sleep_seconds:.0f} seconds until sunset.")
        time.sleep(sleep_seconds)
