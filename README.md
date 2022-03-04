
>Read  
>
照明：          FD 51 B6 08 48 DF   
小夜灯：        FD 51 B6 02 49 DF   
换气：          FD 51 B6 01 49 DF   
自然风：        FD 51 B6 03 49 DF   
弱暖/强暖：     FD 51 B6 04 48 DF   
智能关机：      FD 51 B6 0C 49 DF    

>Send  
>
照明：          FD 03 51 B6 08 48 DF   
小夜灯：        FD 03 51 B6 02 49 DF   
换气：          FD 03 51 B6 01 49 DF   
自然风：        FD 03 51 B6 03 49 DF  
弱暖/强暖：      FD 03 51 B6 04 48 DF   
智能关机：       FD 03 51 B6 0C 49 DF    


```yml
select:
  - platform: warmbath
    name: 'Micoe Bath Heater'

light:
  - platform: micoe.light
    name: 'Micoe Bath Light'
```

<img src="https://user-images.githubusercontent.com/9806325/155892368-0cd0ff88-f1f3-4e58-b9ad-3b31cbd03072.jpeg" width="500">  



#### Debug on macOS
```py
import serial as ser
se = ser.Serial("/dev/cu.usbserial-1410")

data = 'FD 03 51 B6 08 48 DF'
toBytes = bytes.fromhex(data)

res = se.write(toBytes)
print(res)
```

