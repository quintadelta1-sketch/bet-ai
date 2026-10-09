__version__ = "1.0.0"

import threading
from datetime import datetime
from urllib.parse import urlencode

import requests

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView


API_URL = "https://v3.football.api-sports.io"
TIMEZONE = "America/Sao_Paulo"


class BetAIApp(App):

    def build(self):
        self.title = "BET-AI"
        self.games = []

        root = BoxLayout(
            orientation="vertical",
            padding=dp(14),
            spacing=dp(10)
        )

        title = Label(
            text="[b]BET-AI[/b]\nAnálise de futebol",
            markup=True,
            font_size="25sp",
            size_hint_y=None,
            height=dp(75)
        )
        root.add_widget(title)

        subtitle = Label(
            text="Estatísticas e probabilidades esportivas",
            font_size="14sp",
            size_hint_y=None,
            height=dp(35)
        )
        root.add_widget(subtitle)

        self.api_key = TextInput(
            hint_text="Cole sua chave API-Football",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(48)
        )
        root.add_widget(self.api_key)

        self.date_input = TextInput(
            text=datetime.now().strftime("%Y-%m-%d"),
            hint_text="Data: AAAA-MM-DD",
            multiline=False,
            size_hint_y=None,
            height=dp(45)
        )
        root.add_widget(self.date_input)

        refresh_button = Button(
            text="BUSCAR PARTIDAS",
            size_hint_y=None,
            height=dp(50)
        )
        refresh_button.bind(on_press=self.load_games)
        root.add_widget(refresh_button)

        self.status = Label(
            text="Informe sua chave API e busque as partidas.",
            size_hint_y=None,
            height=dp(55)
        )
        root.add_widget(self.status)

        scroll = ScrollView()

        self.results = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None
        )
        self.results.bind(
            minimum_height=self.results.setter("height")
        )

        scroll.add_widget(self.results)
        root.add_widget(scroll)

        footer = Label(
            text="Previsões não são garantias de resultado.",
            size_hint_y=None,
            height=dp(35),
            font_size="12sp"
        )
        root.add_widget(footer)

        return root

    def load_games(self, instance):
        key = self.api_key.text.strip()
        date = self.date_input.text.strip()

        if not key:
            self.status.text = "Informe sua chave API-Football."
            return

        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            self.status.text = "Data inválida. Use AAAA-MM-DD."
            return

        self.status.text = "Buscando partidas..."
        instance.disabled = True

        threading.Thread(
            target=self._fetch_games,
            args=(key, date, instance),
            daemon=True
        ).start()

    def _fetch_games(self, key, date, button):
        try:
            params = urlencode({
                "date": date,
                "timezone": TIMEZONE
            })

            response = requests.get(
                f"{API_URL}/fixtures?{params}",
                headers={"x-apisports-key": key},
                timeout=25
            )

            if response.status_code != 200:
                raise RuntimeError(
                    f"API respondeu HTTP {response.status_code}."
                )

            data = response.json()

            if data.get("errors"):
                raise RuntimeError(
                    "A API informou um erro. "
                    "Confira a chave e os limites do plano."
                )

            fixtures = data.get("response", [])

            games = []
            for item in fixtures:
                fixture = item.get("fixture", {})
                teams = item.get("teams", {})
                status = fixture.get("status", {}).get("short", "")

                if status not in ("NS", "TBD"):
                    continue

                home = teams.get("home", {}).get("name", "Casa")
                away = teams.get("away", {}).get("name", "Visitante")

                games.append({
                    "id": fixture.get("id"),
                    "home": home,
                    "away": away,
                    "league": item.get("league", {}).get(
                        "name", "Competição"
                    ),
                    "time": fixture.get("date", "")
                })

                if len(games) >= 3:
                    break

            Clock.schedule_once(
                lambda dt: self._show_games(games, button)
            )

        except Exception as exc:
            message = str(exc)
            Clock.schedule_once(
                lambda dt: self._show_error(message, button)
            )

    def _show_error(self, message, button):
        self.status.text = "Não foi possível buscar os jogos."
        self.results.clear_widgets()

        self.results.add_widget(
            Label(
                text=message,
                size_hint_y=None,
                height=dp(80)
            )
        )

        button.disabled = False

    def _show_games(self, games, button):
        self.games = games
        self.results.clear_widgets()

        if not games:
            self.status.text = "Nenhuma partida futura encontrada."
        else:
            self.status.text = (
                f"{len(games)} partida(s) encontrada(s)."
            )

        for game in games:
            card = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=dp(125),
                padding=dp(8),
                spacing=dp(4)
            )

            card.add_widget(
                Label(
                    text=f"{game['home']} x {game['away']}",
                    size_hint_y=None,
                    height=dp(35)
                )
            )

            card.add_widget(
                Label(
                    text=game["league"],
                    size_hint_y=None,
                    height=dp(25)
                )
            )

            analyze_button = Button(
                text="CONSULTAR PREVISÃO DA API",
                size_hint_y=None,
                height=dp(45)
            )

            analyze_button.bind(
                on_press=lambda btn, g=game:
                    self.load_prediction(g, btn)
            )

            card.add_widget(analyze_button)
            self.results.add_widget(card)

        button.disabled = False

    def load_prediction(self, game, button):
        key = self.api_key.text.strip()

        if not key:
            self.status.text = "Informe sua chave API."
            return

        button.disabled = True
        button.text = "Consultando..."

        threading.Thread(
            target=self._fetch_prediction,
            args=(key, game, button),
            daemon=True
        ).start()

    def _fetch_prediction(self, key, game, button):
        try:
            response = requests.get(
                f"{API_URL}/predictions",
                params={"fixture": game["id"]},
                headers={"x-apisports-key": key},
                timeout=25
            )

            if response.status_code != 200:
                raise RuntimeError(
                    f"Erro HTTP {response.status_code}."
                )

            data = response.json()

            if data.get("errors"):
                raise RuntimeError(
                    "A API não disponibilizou a previsão. "
                    "Confira seu plano e os limites."
                )

            predictions = data.get("response", [])

            if not predictions:
                raise RuntimeError(
                    "A API não retornou previsão para esta partida."
                )

            prediction = predictions[0].get("predictions", {})
            winner = prediction.get("winner", {})
            percent = prediction.get("percent", {})
            advice = prediction.get("advice", "")

            home_pct = percent.get("home", "N/D")
            draw_pct = percent.get("draw", "N/D")
            away_pct = percent.get("away", "N/D")

            winner_name = winner.get("name") or "Indefinido"

            result = (
                f"{game['home']} x {game['away']}\n\n"
                f"Casa: {home_pct}\n"
                f"Empate: {draw_pct}\n"
                f"Visitante: {away_pct}\n\n"
                f"Favorito indicado pela API: {winner_name}\n\n"
                f"Orientação da API: {advice or 'Não informada'}\n\n"
                "Dados fornecidos pela API-Football. "
                "Não são garantias de resultado."
            )

            Clock.schedule_once(
                lambda dt: self._show_prediction(result, button)
            )

        except Exception as exc:
            message = str(exc)
            Clock.schedule_once(
                lambda dt: self._prediction_error(message, button)
            )

    def _show_prediction(self, result, button):
        self.status.text = result
        button.text = "PREVISÃO CONSULTADA"
        button.disabled = False

    def _prediction_error(self, message, button):
        self.status.text = f"Falha na previsão: {message}"
        button.text = "TENTAR NOVAMENTE"
        button.disabled = False


if __name__ == "__main__":
    BetAIApp().run()
