# Capital Temperature Model

A small Python command-line program that returns the current temperature in a country's capital and its oil and natural-gas reserves. It needs Python 3 and an internet connection, but no package installation or API key. Install Python 3 first if `py --version` reports that no runtime is available.

## Run it

```powershell
py .\capital_temperature.py Iran
```

Or run it without an argument and enter the country when prompted:

```powershell
py .\capital_temperature.py
```

The program has common countries built in and uses REST Countries for other country names. It then uses Open-Meteo to locate the capital and get its current Celsius temperature.

## Oil and gas output

The new section at the end of `capital_temperature.py` downloads country-level **proved reserves** from Our World in Data's copies of the Energy Institute Statistical Review datasets. Oil is shown in tonnes and natural gas in cubic metres, together with each value's latest available year. Proved reserves are commercially recoverable quantities under current conditions; they are not an estimate of all undiscovered resources.

Data sources: [oil proved reserves](https://ourworldindata.org/grapher/oil-proved-reserves) and [natural gas proved reserves](https://ourworldindata.org/grapher/natural-gas-proved-reserves).
