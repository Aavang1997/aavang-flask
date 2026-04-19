from flask import Flask, request, render_template_string
import csv
from datetime import datetime
import requests
from io import StringIO

app = Flask(__name__)

HTML = """
<!doctype html>
<html lang="da">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Telefonnummer</title>
<style>
  body { font-family: Arial, sans-serif; margin: 0; min-height: 100vh; display: grid; place-items: center; background: #f6f6f6; }
  .card { width: min(420px, 92vw); background: #fff; padding: 24px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,.08); text-align: center; }
  p { margin: 0 0 12px; color: #444; font-size: 14px; line-height: 1.4; }
  input { width: 100%; padding: 12px; font-size: 16px; border: 1px solid #ccc; border-radius: 10px; box-sizing: border-box; margin-bottom: 12px; }
  button { width: 100%; margin-top: 12px; padding: 12px; font-size: 16px; border: 0; border-radius: 10px; cursor: pointer; }
  .note { margin-top: 10px; font-size: 12px; color: #666; min-height: 16px; }
  .instagram { margin-top: 32px; text-align: center; }
  .instagram a { color: #1a73e8; }

  /* STEP 1 – PRO FEEDBACK */
  .note.success { color: #1b7f3a; }
  .note.error { color: #b3261e; }

  button[disabled] { opacity: 0.6; cursor: not-allowed; }

  .spinner {
    display: inline-block;
    width: 14px;
    height: 14px;
    border: 2px solid #999;
    border-top-color: transparent;
    border-radius: 50%;
    margin-right: 8px;
    vertical-align: -2px;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin { to { transform: rotate(360deg); } }

.logo {
  width: 400px;      /* 👈 HER styrer du størrelsen */
  max-width: 100%;
  height: auto;
  margin: 0 auto 16px;
  display: block;
}

input.invalid {
  border-color: #b3261e;
}

</style>
</head>
<body>
<main class="card">

  <img src="/static/logo.png" alt="Aavang logo" class="logo" />

  <p>Indtast dit fulde navn og mobilnummer for at modtage en SMS, når der kommer nyt <b>Aavang</b> drip.</p>

  <form method="POST" id="phoneForm">
  <input
    type="text"
    name="fullname"
    placeholder="Indtast dit fulde navn"
    autocomplete="name"
    required
  />

  <input
    type="tel"
    name="phone"
    placeholder="Indtast dit telefonnummer"
    autocomplete="tel"
    required
    inputmode="numeric"
    maxlength="8"
  />

  <button type="submit" id="submitBtn">
    <span class="btnText">Send</span>
  </button>

  <div class="note {{ status_class }}" id="status">{{ status }}</div>
</form>

  <div class="instagram">
    <p>Glem ikke at hoppe ind og follow på Instagram. Klik på linket under</p>
    <p><a href="https://www.instagram.com/aavang.mid/" target="_blank">Aavang Instagram profil</a></p>
  </div>
</main>

<script>
  const form = document.getElementById("phoneForm");
  const btn = document.getElementById("submitBtn");
  const btnText = btn.querySelector(".btnText");
  const statusEl = document.getElementById("status");
  const phoneInput = form.querySelector('input[name="phone"]');
const nameInput = form.querySelector('input[name="fullname"]');

form.addEventListener("submit", (e) => {
  const phone = phoneInput.value.trim();
  const fullname = nameInput.value.trim();

  nameInput.classList.remove("invalid");
  phoneInput.classList.remove("invalid");

  if (fullname.length < 2) {
    e.preventDefault();
    statusEl.textContent = "Indtast dit fulde navn.";
    statusEl.className = "note error";
    nameInput.classList.add("invalid");
    return;
  }

  if (!/^\\d{8}$/.test(phone)) {
    e.preventDefault();
    statusEl.textContent = "Indtast et gyldigt telefonnummer (8 cifre).";
    statusEl.className = "note error";
    phoneInput.classList.add("invalid");
    return;
  }

  statusEl.textContent = "";
  btn.disabled = true;
  btnText.innerHTML = '<span class="spinner"></span>Sender...';
});
</script>

</body>
</html>
"""

def phone_exists(phone):
    SHEET_URL = "https://docs.google.com/spreadsheets/d/13rOo0e3Y7h1yYo3BzwbBdAkRFjLlFCDGmi2jWvcJL8c/export?format=csv"

    try:
        r = requests.get(SHEET_URL, timeout=5)
        r.raise_for_status()

        from io import StringIO
        import csv

        csv_data = StringIO(r.text)
        reader = csv.DictReader(csv_data)

        for row in reader:
            if row["Telefonnummer"].strip() == phone.strip():
                return True

    except Exception as e:
        print("Fejl ved tjek af sheet:", e)

    return False

@app.route("/", methods=["GET", "POST"])
def index():
    status = ""
    status_class = ""

    if request.method == "POST":
        fullname = (request.form.get("fullname") or "").strip()
        phone = (request.form.get("phone") or "").strip()

        if phone_exists(phone):
            status = "Dette telefonnummer er allerede tilmeldt."
            status_class = "error"
            return render_template_string(HTML, status=status, status_class=status_class)

        if len(fullname) < 2:
            status = "Indtast dit fulde navn."
            status_class = "error"
            return render_template_string(HTML, status=status, status_class=status_class)

        if not (phone.isdigit() and len(phone) == 8):
            status = "Indtast et gyldigt telefonnummer (8 cifre)."
            status_class = "error"
            return render_template_string(HTML, status=status, status_class=status_class)

        now = datetime.now()
        date = now.strftime("%d-%m-%Y")
        time = now.strftime("%H:%M")

        FORM_ACTION_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdihXEliELHSuYHQW08MtquCkLC-q2SzMhKBRhwGZjsfO4N0A/formResponse"
        ENTRY_NAME = "entry.1789850509"
        ENTRY_DATE = "entry.320320826"
        ENTRY_TIME = "entry.1767503633"
        ENTRY_PHONE = "entry.1135538317"

        payload = {
            ENTRY_NAME: fullname,
            ENTRY_DATE: date,
            ENTRY_TIME: time,
            ENTRY_PHONE: phone,
        }

        try:
            requests.post(FORM_ACTION_URL, data=payload, timeout=10)
            status = "Tak! Dit navn og nummer er gemt."
            status_class = "success"
        except requests.RequestException:
            status = "Noget gik galt. Prøv igen."
            status_class = "error"

    return render_template_string(HTML, status=status, status_class=status_class)

if __name__ == "__main__":
    app.run(debug=True)
