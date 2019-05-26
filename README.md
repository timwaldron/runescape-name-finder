**I have discontinued this project after the realization that if someone creates a RuneScape account and doesn't train any skills, it will not register that account on the hiscores. Still pushing this to GitHub as someone, somewhere might learn something.**  

# RuneScape Name Finder
I decided to build this project in Python because I'm not familiar with the language and trying to figure out asynchronous HTTP requests is fun.

## How it works
This application loads the file `names-list.txt` and checks both the [RuneScape 3](https://secure.runescape.com/m=hiscore/ranking) & [OldSchool RuneScape](https://secure.runescape.com/m=hiscore_oldschool/overall.ws) hiscores asynchronously and gauges whether the HTTP response is `200`, `404` or `503`. It stores the results in the `OSRS_Data` and `RS3_Data` directories.
+ `200 Response`: Player exists/username is taken
+ `404 Response`: Player doesn't exist/username may be available.
+ `503 Response`: Service unavailable (probably due to the number of requests).  
<br>

## Screenshots
![Checking RS3 Names](/images/rs-name-finder-1.png)  
<br>
![Checking RS3 Names](/images/rs-name-finder-2.png)  
<br>
![Checking RS3 Names](/images/rs-name-finder-3.png)