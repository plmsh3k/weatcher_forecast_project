import requests
import matplotlib.pyplot as plt
import datetime
import random


class Forecast:
    def __init__(self, data):
        if data is None:
            raise ValueError("No data provided for weather information.")
        self.forecast_day = data['forecast']['forecastday'][0]['day']
        self.forecast_hours = data['forecast']['forecastday'][0]['hour']
        self.display()

    def display(self):
        raise NotImplementedError("Subclasses must implement this method.")

class BasicForecast(Forecast):
    def display(self):
        print(f"Today's temperature: {self.forecast_day['avgtemp_c']}°C")
        print(f"Conditions: {self.forecast_day['condition']['text']}")

class AdvancedForecast(Forecast):
    def display(self):
        print("Today's temperature:")
        for hour in self.forecast_hours:
            print(f"{hour['time'][11:]} - Temp: {hour['temp_c']}°C, Condition: {hour['condition']['text']}")

class PremiumForecast(Forecast):
    def display(self):
        print("Detailed Forecast with Predictive Analysis:")
        print(f"Today's temperature: {self.forecast_day['avgtemp_c']}°C")
        for hour in self.forecast_hours:
            feels_like = hour.get('feelslike_c', 'N/A')
            print(f"{hour['time'][11:]} - Temp: {hour['temp_c']}°C, Feels Like: {feels_like}°C")


class WeatherAPI:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_weather_by_date(self, date):
        response = requests.get(f"https://api.weatherapi.com/v1/history.json?key={self.api_key}&q=Turku&dt={date}")
        return response.json()


class WeatherData:
    def __init__(self, data):
        if data is None:
            raise ValueError("No data provided for weather information.")
        self.location = data['location']
        self.forecast = data['forecast']['forecastday'][0]

    def display_basic_info(self):
        location_info = (self.location['name'], self.location['region'], self.location['country'])
        weather_info = self.forecast['day']
        condition = weather_info['condition']['text']
        max_temp = weather_info['maxtemp_c']
        min_temp = weather_info['mintemp_c']
        average_temp = weather_info['avgtemp_c']
        humidity = weather_info['avghumidity']
        uv_index = weather_info['uv']

        print(f"Weather Information for {location_info[0]}, {location_info[1]}, {location_info[2]}:")
        print(f"Condition: {condition}")
        print(f"Max Temp: {max_temp}°C, Min Temp: {min_temp}°C, Avg Temp: {average_temp}°C")
        print(f"Humidity: {humidity}%")
        print(f"UV Index: {uv_index}")

    def display_hourly_info(self):
        print("Hourly Forecast:")
        for hour in self.forecast['hour']:
            time = hour['time']
            temp = hour['temp_c']
            condition = hour['condition']['text']
            print(f"Time: {time}, Temperature: {temp}°C, Condition: {condition}")

    def plot_daily_temperature(self):
        times = [hour['time'][11:] for hour in self.forecast['hour']]
        temperatures = [hour['temp_c'] for hour in self.forecast['hour']]

        plt.figure(figsize=(10, 5))
        plt.plot(times, temperatures, marker='o', linestyle='-', color='b')
        plt.title(f"Temperature Trend for {self.forecast['date']}")
        plt.xlabel('Time of Day')
        plt.ylabel('Temperature (°C)')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def predict_future_weather(self, target_date_str):
        current_date = datetime.datetime.now()
        target_date = datetime.datetime.strptime(target_date_str, '%Y-%m-%d')

        day_difference = (target_date - current_date).days

        if day_difference < 0:
            print("Predicting for a past day using data from one day earlier.")
            base_temp = self.forecast['day']['avgtemp_c']
            fluctuation = random.uniform(-2, 2)
            predicted_temp = base_temp + fluctuation
        else:
            print("Predicting for a future day.")
            base_temp = self.forecast['day']['avgtemp_c']
            total_fluctuation = 0
            for _ in range(day_difference):
                fluctuation = random.uniform(-2, 2)
                total_fluctuation += fluctuation

            predicted_temp = base_temp + total_fluctuation

        print(f"Predicted average temperature for {target_date_str}: {predicted_temp:.1f}°C")


def validate_date(date_str):
    try:
        datetime.datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def is_future_date(date_str):
    today = datetime.datetime.now()
    date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    return date > today


def is_more_than_one_year_ago(date_str):
    today = datetime.datetime.now()
    one_year_ago = today - datetime.timedelta(days=365)
    input_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    return input_date < one_year_ago


class Application:
    def __init__(self):
        self.api = WeatherAPI('35f8506bfae44bc2a7f131404241504')

    def main_menu(self):
        while True:
            print("\nChoose an action:")
            print("1: Check weather by date")
            print("2: Detailed hourly weather")
            print("3: Show temperature graph")
            print("4: Predict weather for a specific day")
            print("5: Exit program")
            choice = input("Enter your choice: ")

            if choice == '1':
                date = input("Enter the date (YYYY-MM-DD): ")
                if not validate_date(date):
                    print("Invalid date format. Please enter the date in YYYY-MM-DD format.")
                    continue
                if is_future_date(date):
                    weather_data = self.api.get_weather_by_date(datetime.datetime.now().strftime('%Y-%m-%d'))
                    weather = WeatherData(weather_data)
                    weather.predict_future_weather(date)
                elif is_more_than_one_year_ago(date):
                    print("historical data only available up until 1 year in the past")
                else:
                    print("Select Forecast Type:")
                    print("a: Basic Forecast")
                    print("b: Advanced Forecast")
                    print("c: Premium Forecast")

                    forecast_type = input("Enter forecast type: ")
                    weather_data = self.api.get_weather_by_date(date)

                    if forecast_type == "a":
                        forecast = BasicForecast(weather_data)
                    elif forecast_type == "b":
                        forecast = AdvancedForecast(weather_data)
                    elif forecast_type == "c":
                        forecast = PremiumForecast(weather_data)
                    else:
                        print("Invalid forecast type selected.")
                        return

                    forecast.display()
            elif choice == '2':
                date = input("Enter the date for hourly details (YYYY-MM-DD): ")
                if not validate_date(date):
                    print("Invalid date format. Please enter the date in YYYY-MM-DD format.")
                    continue
                if is_future_date(date):
                    print("feature not available for future dates")
                elif is_more_than_one_year_ago(date):
                    print("historical data only available up until 1 year in the past")
                else:
                    weather_data = self.api.get_weather_by_date(date)
                    weather = WeatherData(weather_data)
                    weather.display_hourly_info()
            elif choice == '3':
                date = input("Enter the date for temperature graph (YYYY-MM-DD): ")
                if not validate_date(date):
                    print("Invalid date format. Please enter the date in YYYY-MM-DD format.")
                    continue
                if is_future_date(date):
                    print("feature not available for future dates")
                elif is_more_than_one_year_ago(date):
                    print("historical data only available up until 1 year in the past")
                else:
                    weather_data = self.api.get_weather_by_date(date)
                    weather = WeatherData(weather_data)
                    weather.plot_daily_temperature()
            elif choice == '4':
                date = input("Enter the date for prediction (YYYY-MM-DD): ")
                if not validate_date(date):
                    print("Invalid date format. Please enter the date in YYYY-MM-DD format.")
                    continue
                elif is_more_than_one_year_ago(date):
                    print("historical data only available up until 1 year in the past")
                else:
                    weather_data = self.api.get_weather_by_date(datetime.datetime.now().strftime('%Y-%m-%d'))
                    weather = WeatherData(weather_data)
                    weather.predict_future_weather(date)
            elif choice == '5':
                print("Exiting program.")
                break
            else:
                print("Invalid input, please try again.")


if __name__ == "__main__":
    app = Application()
    app.main_menu()

if __name__ == "__main__":
    app = Application()
    app.main_menu()
