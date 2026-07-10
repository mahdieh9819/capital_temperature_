# Capital Temperature Model

A small Python command-line program that returns the current temperature in a country's capital. It needs Python 3 and an internet connection, but no package installation or API key. Install Python 3 first if `py --version` reports that no runtime is available.

## Run it

```powershell
py .\capital_temperature.py Iran
```

Or run it without an argument and enter the country when prompted:

```powershell
py .\capital_temperature.py
```

The program has common countries built in and uses REST Countries for other country names. It then uses Open-Meteo to locate the capital and get its current Celsius temperature.
