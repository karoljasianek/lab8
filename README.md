# Laboratorium 8: regresja – ile wyda klient, który zostaje?

Eksploracja danych · zajęcia 8 · Karol Jasianek

## Co oddaję

| Element | Gdzie |
|---|---|
| Repozytorium (notatnik wykonany od początku) | https://github.com/karoljasianek/lab8 |
| Notatnik z zadaniami Z1–Z9, D1–D2 i odpowiedziami | [`lab8_student.ipynb`](lab8_student.ipynb) |
| D1–D2 | ostatnia komórka notatnika oraz [niżej](#zadanie-domowe) |
| D3 (dla chętnych): aplikacja na Render | https://ryzyko-i-wartosc.onrender.com |
| Kod aplikacji D3 | [`app.py`](app.py), ustawienia wdrożenia w [`render.yaml`](render.yaml) |

> Aplikacja działa na darmowym planie Render: po dłuższej bezczynności usypia, więc pierwsze otwarcie może trwać ok. 30–60 s.

## Uzupełnione luki (6)

| Zadanie | Luka | Wartość |
|---|---|---|
| Z1 | potęga w mianowniku wzoru na b | `dx ** 2` |
| Z2 | klienci, którzy zostali | `df["odszedl"] == 0` |
| Z5 | jedna cecha regresji prostej | `ucz[["wydatki_zl"]]` |
| Z7 | powrót z logarytmu do złotówek | `np.exp(...)` |
| Z8 | min. liczba klientów w liściu (jak w lab. 7) | `min_samples_leaf=20` |
| Z9 | marża 25% | `0.25` |

## Wyniki kontrolne (zgodne z kartą)

| Zad. | Co | Wynik |
|---|---|---|
| Z1 | b, a, MAE (pięciu klientów) | 0,45; 60; 80 zł |
| Z2 | zostało klientów; korelacja (bez firm) | 825; 0,797 |
| Z3 | nachylenie z firmami / bez firm | 0,476 / 0,530 |
| Z4 | MAE średniej (zbiór testowy) | 799,6 zł |
| Z5 | regresja prosta: a, b, MAE, R² | 27,4; 0,522; 375,1 zł; 0,681 |
| Z6 | wieloraka: MAE; współczynnik `dni_od_ostatniego` | 363,1 zł; −1,894 |
| Z7 | log: współczynnik `log_wydatki`; MAE | 0,516; 342,3 zł |
| Z8 | drzewo regresyjne gł. 3: MAE | 398,7 zł |
| Z9 | kuponów: stara / nowa reguła | 429 / 170 |

## Odpowiedzi

**Z1.** b = 0,45: każda złotówka więcej wydana w roku to średnio 0,45 zł więcej w kolejnym półroczu (100 zł → +45 zł). Klient, który wydał w roku 1000 zł: 60 + 0,45 · 1000 = **510 zł** w półroczu. MAE = 80 zł.

**Z2–Z3. Kogo modelujemy i dlaczego.** Z 1206 klientów zostało 825. Modelujemy tylko ich, bo `wydatki_6m = 0` u klientów, którzy odeszli, wynika z odejścia, a to przewiduje model z lab. 7. Usuwamy też 4 konta firmowe (38–74 tys. zł rocznie, 46–74 zamówienia), więc modelujemy **821 klientów indywidualnych**. Firmy to inna skala i inny proces (kontrakty, handlowiec), a 4 obserwacje to za mało, żeby się czegoś o nich nauczyć. Konto 101106 (52 tys. zł w roku, tylko 2140 zł w półroczu) to obserwacja wpływowa: z firmami nachylenie wynosi 0,476, bez nich 0,530. Bez firm zależność jest dodatnia i prawie liniowa (r = 0,797), a rozrzut rośnie z wielkością klienta.

**Z5. Interpretacja b; wykres błędów.** Model: wydatki_6m = 27,4 + 0,522 · wydatki_zl. Każde 100 zł wydane w roku to ok. 52 zł w kolejnym półroczu: klient utrzymuje swoje tempo. MAE spada z 799,6 zł do 375,1 zł (o 424,5 zł, −53%), a R² wynosi 0,681. Wykres błędów ma kształt **lejka**: średni błąd to ok. 160 zł przy prognozach < 500 zł, ok. 340 zł przy 500–1500 zł i ok. 940 zł powyżej 1500 zł. Błąd rośnie z wielkością klienta, co prowadzi do modelu na logarytmach.

**Z6. Znak przy dniach; dlaczego spadł współczynnik wydatków.** Współczynnik przy `dni_od_ostatniego` jest **ujemny, −1,894**: każdy dzień od ostatniego zamówienia (przy pozostałych cechach bez zmian) obniża prognozę o ok. 1,89 zł (30 dni → ok. −57 zł). Klient „stygnie”. Współczynnik przy `wydatki_zl` spadł z 0,522 do **0,309**, bo wydatki = liczba zamówień × koszyk, a te cechy są ze sobą powiązane (korelacja 0,54 i 0,78). Część efektu przejęły `liczba_zamowien` (+8,5 zł) i `sredni_koszyk_zl` (+1,81 zł). Nie wynika z tego „podnieśmy wydatki o 1 zł”: to korelacja, nie przyczyna. MAE modelu wielorakiego to 363,1 zł.

**Z7. Interpretacja w procentach.** Wydatki w roku wyższe o 1% dają prognozę wyższą o ok. **0,52%** (+10% wydatków → ok. +5%). Koszyk wyższy o 1% to ok. +0,49%. Każdy dzień bez zamówienia to ok. **−0,3%** prognozy (30 dni → ok. −9%, 170 dni → ok. −41%). Model log ma **najmniejszy MAE: 342,3 zł**.

**Z8. Dlaczego drzewo przegrywa.** Drzewo o głębokości 3 daje najwyżej 8 różnych prognoz (na teście 7), bo wszyscy w liściu dostają tę samą średnią. Prosta daje inną prognozę każdemu klientowi. Zależność jest płynna i prawie liniowa, więc „schodki” ją zgrubnie przybliżają. Drzewo nie wychodzi też poza średnie z liści (maks. prognoza ok. 5140 zł, maks. klient ok. 7030 zł). MAE drzewa to 398,7 zł wobec 342,3 zł w modelu log.

**Z9. Kogo nowa reguła pomija, kogo dodaje.** Stara reguła daje 429 kuponów, nowa 170. W obu jest 125 klientów, więc adresata zmienia 349 kuponów: 304 klientów traci kupon, a 45 go zyskuje. Nowa reguła **pomija** klientów z wysokim ryzykiem, ale małymi wydatkami (np. 100948: 60 zł w roku, ryzyko 0,86, prognoza 46 zł, więc kupon za 30 zł się nie zwraca). **Dodaje** klientów z umiarkowanym ryzykiem (0,22), ale dużą wartością (np. 100090: 9771 zł w roku, prognoza 4432 zł, zysk z kuponu +114 zł). Klienci wysokiego ryzyka są warci średnio **133 zł** rocznej marży, a nie zakładane 250 zł. Oczekiwany zysk: stara reguła −2017 zł, nowa +2326 zł.

## Zadanie domowe

**D1.** Model z Z7: ln(wydatki_6m) = 0,4205 + 0,5163 · ln(wydatki_rok) + 0,4884 · ln(koszyk) − 0,003068 · dni, czyli wydatki_6m ≈ 1,523 · wydatki_rok^0,516 · koszyk^0,488 · e^(−0,00307 · dni).

> „Klient, który w ostatnim roku wydał 1500 zł, ze średnim koszykiem 150 zł i ostatnim zamówieniem 30 dni temu, wyda w kolejnym półroczu ok. **700 zł**. Ten sam klient z ostatnim zamówieniem 200 dni temu wyda ok. **416 zł** (ok. 40% mniej). Każdy 1% wyższych wydatków w roku to ok. +0,5% w półroczu, a każdy dzień bez zamówienia to ok. −0,3%.”

**D2.** Przy skuteczności kuponu 15% kupon opłaca się, gdy ryzyko × prognoza > 400 zł. Według nowej reguły dostaje go **19 klientów** (przy 30% było ich 170).

**D3.** Aplikacja https://ryzyko-i-wartosc.onrender.com (kod w [`app.py`](app.py)). Do kalkulatora ryzyka z lab. 7 dodałem:
- **prognozowane wydatki w półroczu** z modelu logarytmicznego z Z7 (te same dane, podział i cechy co w notatniku),
- **oczekiwany zysk z kuponu** = ryzyko × skuteczność × 0,25 × 2 × prognoza − 30 zł, z suwakiem skuteczności kuponu,
- decyzję według wartości klienta (lab. 8) obok decyzji według progu ryzyka (lab. 7),
- rozwijany opis wzoru ze współczynnikami i podstawionymi liczbami.

Kontrola: 10 zamówień × 150 zł, 30 dni → aplikacja pokazuje 700 zł, tak jak w D1.

## Uruchomienie

```bash
pip install -r requirements.txt
jupyter notebook lab8_student.ipynb      # albo Codespaces, jądro Python 3
streamlit run app.py                     # aplikacja D3, port 8501
```

W `requirements.txt` streamlit jest podniesiony do 1.67.0, bo wersja 1.50.0 z szablonu nie instaluje się razem z pandas 3.0.5. Doszedł też matplotlib, którego potrzebuje notatnik.

## Pliki

| Plik | Co to jest |
|---|---|
| `lab8_student.ipynb` | notatnik z zadaniami Z1–Z9, odpowiedziami i D1–D2 |
| `klienci_wartosc.csv` | 1206 klientów: dane z lab. 7 + `wydatki_6m` (dane syntetyczne) |
| `pieciu_klientow.csv` | 5 klientów do rozgrzewki (Z1) |
| `app.py` | aplikacja Streamlit: ryzyko odejścia + wartość klienta + zysk z kuponu (D3) |
| `requirements.txt`, `render.yaml` | zależności i konfiguracja wdrożenia na Render |
