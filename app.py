"""Kalkulator ryzyka i wartości klienta: drzewo decyzyjne z lab. 7 + regresja logarytmiczna z lab. 8."""
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.model_selection import train_test_split

CECHY = ["liczba_zamowien", "wydatki_zl", "sredni_koszyk_zl", "dni_od_ostatniego",
         "udzial_promocji", "udzial_internet", "liczba_kategorii", "zwroty"]
KOSZT_KUPONU = 30.0
MARZA = 0.25


def cechy_log(d):
    return pd.DataFrame({"log_wydatki": np.log(d["wydatki_zl"]), "log_koszyk": np.log(d["sredni_koszyk_zl"]),
                         "dni_od_ostatniego": d["dni_od_ostatniego"]})


@st.cache_resource
def naucz_modele():
    df = pd.read_csv("klienci_wartosc.csv", sep=";", decimal=",")
    # lab. 7: ryzyko odejścia
    X_ucz, X_test, y_ucz, y_test = train_test_split(df[CECHY], df["odszedl"], test_size=0.3,
                                                    stratify=df["odszedl"], random_state=42)
    model = DecisionTreeClassifier(max_depth=3, min_samples_leaf=20, random_state=0).fit(X_ucz, y_ucz)
    # lab. 8 (Z7): ile wyda w półroczu klient indywidualny, który zostaje
    ind = df[(df["odszedl"] == 0) & (df["wydatki_zl"] <= 20000)]
    ucz, _ = train_test_split(ind, test_size=0.3, random_state=42)
    logm = LinearRegression().fit(cechy_log(ucz), np.log(ucz["wydatki_6m"]))
    return model, model.score(X_test, y_test), logm


model, trafnosc, logm = naucz_modele()

st.title("Kto odejdzie i ile jest wart?")
st.caption(f"Ryzyko: drzewo decyzyjne (głębokość 3, min. 20 klientów w liściu), trafność na zbiorze testowym {100 * trafnosc:.1f}%. "
           "Wartość: regresja na logarytmach (lab. 8, Z7). Dane syntetyczne.")

st.sidebar.header("Klient")
liczba = st.sidebar.number_input("liczba zamówień (12 mies.)", 1, 60, 3)
koszyk = st.sidebar.number_input("średni koszyk [zł]", 10.0, 5000.0, 200.0, step=10.0)
dni = st.sidebar.slider("dni od ostatniego zamówienia", 0, 364, 60)
promo = st.sidebar.slider("udział zamówień z promocją", 0.0, 1.0, 0.3)
net = st.sidebar.slider("udział zamówień przez internet", 0.0, 1.0, 0.5)
kat = st.sidebar.slider("liczba kategorii", 1, 5, 2)
zwroty = st.sidebar.number_input("zwroty", 0, 20, 0)
st.sidebar.header("Kupon")
prog = st.sidebar.slider("próg ryzyka (reguła z lab. 7)", 0.05, 0.95, 0.40, step=0.05)
skutecznosc = st.sidebar.slider("skuteczność kuponu", 0.05, 0.60, 0.30, step=0.05)

klient = pd.DataFrame([{"liczba_zamowien": liczba, "wydatki_zl": liczba * koszyk, "sredni_koszyk_zl": koszyk,
                        "dni_od_ostatniego": dni, "udzial_promocji": promo, "udzial_internet": net,
                        "liczba_kategorii": kat, "zwroty": zwroty}])[CECHY]
ryzyko = model.predict_proba(klient)[0, 1]
wartosc_6m = float(np.exp(logm.predict(cechy_log(klient)))[0])
zysk = ryzyko * skutecznosc * MARZA * 2 * wartosc_6m - KOSZT_KUPONU

c1, c2, c3 = st.columns(3)
c1.metric("ryzyko odejścia", f"{100 * ryzyko:.0f}%")
c2.metric("prognozowane wydatki w półroczu", f"{wartosc_6m:,.0f} zł".replace(",", " "))
c3.metric("oczekiwany zysk z kuponu", f"{zysk:+,.0f} zł".replace(",", " "))

d1, d2 = st.columns(2)
d1.metric("decyzja wg wartości (lab. 8)", "wyślij kupon" if zysk > 0 else "bez kuponu")
d2.metric(f"decyzja wg progu ryzyka {prog:.2f} (lab. 7)", "wyślij kupon" if ryzyko >= prog else "bez kuponu")

a, (b_w, b_k, b_d) = logm.intercept_, logm.coef_
with st.expander("Jak liczymy wartość i zysk?"):
    st.markdown(
        f"**Prognoza (model z Z7):** ln(wydatki_6m) = {a:.4f} + {b_w:.4f}·ln(wydatki_rok) + {b_k:.4f}·ln(koszyk) "
        f"{b_d:+.5f}·dni, czyli wydatki_6m = exp(…). Wydatki w roku = liczba zamówień × koszyk = "
        f"{liczba * koszyk:,.0f} zł.\n\n".replace(",", " ")
        + f"**Zysk z kuponu** = ryzyko × skuteczność × marża {MARZA:.0%} × 2 półrocza × prognoza − {KOSZT_KUPONU:.0f} zł = "
        f"{ryzyko:.3f} × {skutecznosc:.2f} × {MARZA} × 2 × {wartosc_6m:.0f} − {KOSZT_KUPONU:.0f} = **{zysk:.2f} zł**.")

# ścieżka klienta w drzewie
st.subheader("Dlaczego? Ścieżka w drzewie")
drzewo = model.tree_
wezly = model.decision_path(klient).indices
for w in wezly:
    if drzewo.children_left[w] == -1:
        n0, n1 = drzewo.value[w][0]
        st.write(f"**Liść:** w danych uczących odeszło {100 * n1 / (n0 + n1):.0f}% klientów z tej grupy ({drzewo.n_node_samples[w]} klientów).")
    else:
        cecha, prog_w = CECHY[drzewo.feature[w]], drzewo.threshold[w]
        tak = klient.iloc[0][cecha] <= prog_w
        st.write(f"{cecha} = {klient.iloc[0][cecha]:.2f} {'≤' if tak else '>'} {prog_w:.2f}")

with st.expander("Całe drzewo jako reguły"):
    st.code(export_text(model, feature_names=CECHY))
