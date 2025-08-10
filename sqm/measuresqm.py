import socket
import time
import csv
from astral.sun import sun, dusk, dawn
from astral import LocationInfo
from astral import moon
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# 로그 기록하기
def log(message):
    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("SQMlog.txt","a",encoding="utf-8") as f:
        f.write(f"{timestamp} | {message}\n")

# 밤하늘 정보 불러오기
def nighttime(city,country,timezone,latitude,longitude):
    location=LocationInfo(city,country,timezone,latitude=latitude, longitude=longitude)
    now=datetime.now(ZoneInfo(location.timezone))

    sun_today=sun(location.observer, date=now.date(), tzinfo=location.timezone)
    sun_tomorrow=sun(location.observer, date=now.date()+timedelta(days=1), tzinfo=location.timezone)

    sunset=sun_today["sunset"]
    sunrise=sun_tomorrow["sunrise"]

    dusk_today=dusk(location.observer, date=now.date(), tzinfo=location.timezone, depression=18)
    dawn_tomorrow=dawn(location.observer, date=now.date(), tzinfo=location.timezone, depression=18)

    moon_phase=moon.phase(now)

    return now, sunset, sunrise, dusk_today, dawn_tomorrow, sun_today, sun_tomorrow, moon_phase, location.timezone

# 시리얼번호 가져오기
def serialnumber(IP,PORT):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)
        s.connect((IP,PORT))
        s.sendall(b'Rx\r\n')
        data=s.recv(1024)
        if data:
            decoded=data.decode(errors="ignore").strip()
            parts=decoded.split(",")
            if len(parts)>=7:
                serial=parts[6].strip()
                return serial
            else:
                log("WARNING: Serial number not found in response.")
                return "unknown"
        else:
            log("WARNING: No data received while fetching serial number.")
            return "unknown"

# 데이터 평균값값 저장하기
def average(avg_sun,avg_twilight,moon_phase,city,serial):
    today = datetime.now().strftime("%Y-%m-%d")
    filename=f"sqmavg_{city}_{serial}.csv"
    with open(filename,"a",newline="",encoding="utf-8") as f:
        writer=csv.writer(f)
        writer.writerow([today,avg_sun,avg_twilight,moon_phase])

# 데이터 일일값 저장하기
def daily(brightness_values, temperature_values, photon_values, timestamps, sunset, city, serial, moon_phase, location_timezone):
    sunset_date = sunset.date().strftime("%Y-%m-%d")
    filename=f"{sunset_date}_{city}_{serial}.csv"

    with open(filename,"w",newline="",encoding="utf-8") as f:
        writer=csv.writer(f)
        writer.writerow(["timestamp","brightness(m)","temperature(C)","photon(Hz)"])
        for ts, bri, temp, pho in zip(timestamps, brightness_values, temperature_values, photon_values):
            writer.writerow([ts,bri, temp, pho])

# 데이터 측정하기
def measurement(IP,PORT,timeinterval,sunset,now,sunrise,dusk_today,dawn_tomorrow,city,serial,moon_phase, location_timezone):
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
        twilight_brightnesses=[
            bri for bri, ts in zip(brightness_values,timestamps)
            if dusk_today <= datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").replace(tzinfo=location_timezone) <= dawn_tomorrow
        ]

        if twilight_brightnesses:
            avg_twilight=sum(twilight_brightnesses)/len(twilight_brightnesses)
        else:
            avg_twilight=None
            log("WARNING: No data in astronomical twilight range.")
            
        average(avg_brightness,avg_twilight,moon_phase,city,serial)
        daily(brightness_values,temperature_values,photon_values,timestamps,sunset,city,serial,moon_phase,location_timezone)
        print(f"Average brightness saved: {avg_brightness}")
        log(f"average brightness saved: {avg_brightness}")
        print(f"Daily data saved")
        log(f"Daily data saved {i+1}")
    else:
        log("No valid brightness data collected.")

measured_today=False

city="Daejeon"
country="South Korea"
timezone="Asia/Seoul"
latitude=36.3667
longitude=127.3556

IP='192.168.0.7'
PORT=10001
timeinterval=30

serial=serialnumber(IP,PORT)

while True:
    now, sunset, sunrise, dusk_today, dawn_tomorrow, sun_today, sun_tomorrow, moon_phase, location_timezone = nighttime(city,country,timezone,latitude,longitude)

    if sunset <= now < sunrise:
        if not measured_today:
            try:
               measurement(IP,PORT,timeinterval,sunset,now,sunrise,dusk_today,dawn_tomorrow,city,serial,moon_phase,location_timezone)
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
