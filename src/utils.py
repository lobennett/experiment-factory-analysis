import typing
import requests
import os


def fetch_data(BATTERY_ID: int):
    JAIME_TOKEN = os.getenv("JAIME_TOKEN")
    MCKENZIE_TOKEN = os.getenv("MCKENZIE_TOKEN")
    tokens = [JAIME_TOKEN, MCKENZIE_TOKEN]

    if BATTERY_ID:
        url = f"http://expfactory.org/new_api/results/{BATTERY_ID}"
    else:
        print("No BATTERY_ID provided!")
        return

    with requests.Session() as sess:
        for token in tokens:
            sess.headers.update(
                {"Authorization": f"token {token}", "Cache-Control": "no-cache"}
            )
            while url:
                try:
                    response = sess.get(url)
                    response.raise_for_status()
                    data = response.json()
                    yield data
                    url = data.get("next")
                except requests.HTTPError as e:
                    if e.response.status_code == 403:
                        print(
                            f"Access forbidden with token, trying next token: {token}"
                        )
                        break
                    else:
                        print(f"HTTP error fetching data from {url}: {e}")
                        yield None
                except requests.RequestException as e:
                    print(f"Error fetching data from {url}: {e}")
                    yield None
