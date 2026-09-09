# Expense Tracker

## 1. Problemformulering

Det kan være svært at bevare overblikket over personlige udgifter, især når brugeren manuelt skal registrere, kategorisere og gennemgå sine køb. Små daglige udgifter kan nemt blive glemt, og inkonsekvent kategorisering kan gøre det vanskeligt at forstå, hvad pengene bliver brugt på.

Formålet med Expense Tracker er at tilbyde en enkel webbaseret applikation, hvor brugeren kan registrere, administrere og analysere sine udgifter.

Hver udgift indeholder:

- beskrivelse
- beløb
- dato
- kategori

For at reducere mængden af manuelt arbejde indeholder applikationen en AI-assistent, som foreslår en passende kategori baseret på udgiftens beskrivelse.

Eksempel:

- Netto → Mad
- Matas → Kosmetik og personlig pleje
- DSB → Transport
- Netflix → Underholdning

Brugeren kan acceptere den foreslåede kategori eller selv vælge en anden kategori.

Applikationen skal samtidig give brugeren et visuelt overblik over månedens udgifter, herunder hvor stor en procentdel hver kategori udgør af det samlede forbrug.

Brugeren skal desuden kunne registrere forventede fremtidige udgifter, eksempelvis abonnementer eller planlagte betalinger. Når datoen for en fremtidig udgift nås, skal brugeren kunne bekræfte, om udgiften faktisk fandt sted, før den registreres som en reel udgift.

---

# 2. Funktioner og acceptkriterier

## Feature 1 – Tilføj en udgift

Brugeren kan oprette en ny udgift ved at indtaste:

- beskrivelse
- beløb
- dato

### Acceptkriterier

**Scenario: Udgiften oprettes korrekt**

**Given** brugeren befinder sig på siden til registrering af en udgift<br>
**When** brugeren indtaster en gyldig beskrivelse, et beløb og en dato og gemmer udgiften<br>
**Then** skal udgiften gemmes og vises på brugerens liste over udgifter.

**Scenario: Obligatoriske oplysninger mangler**

**Given** brugeren er ved at oprette en ny udgift<br>
**When** brugeren forsøger at gemme udgiften uden at udfylde de obligatoriske felter<br>
**Then** skal systemet vise en valideringsbesked, og udgiften må ikke gemmes.

---

## Feature 2 – Vælg og få foreslået en kategori

Når brugeren indtaster en beskrivelse af udgiften, skal AI-assistenten foreslå en relevant kategori.

Eksempel:

**Beskrivelse:** Netto<br>
**Foreslået kategori:** Mad

Mulige kategorier:

- Mad
- Transport
- Bolig
- Underholdning
- Kosmetik og personlig pleje
- Shopping
- Abonnementer
- Andet

Brugeren skal altid kunne ændre den foreslåede kategori.

### Acceptkriterier

**Scenario: AI foreslår en kategori**

**Given** brugeren er ved at oprette en udgift<br>
**When** brugeren indtaster en beskrivelse af udgiften<br>
**Then** skal systemet foreslå en relevant kategori baseret på beskrivelsen.

**Scenario: Brugeren ændrer den foreslåede kategori**

**Given** systemet har foreslået en kategori<br>
**When** brugeren vælger en anden kategori<br>
**Then** skal den kategori, som brugeren selv har valgt, gemmes sammen med udgiften.

---

## Feature 3 – Visualisering af månedlige udgifter

Applikationen skal give brugeren et visuelt overblik over udgifterne for en valgt måned.

Udgifterne skal grupperes efter kategori og vises i et diagram.

Diagrammet skal både vise:

- beløbet brugt inden for hver kategori
- kategoriens procentdel af månedens samlede udgifter

Eksempel:

- Mad – 2.500 DKK – 54 %
- Transport – 700 DKK – 15 %
- Underholdning – 450 DKK – 10 %
- Shopping – 1.000 DKK – 21 %

Et cirkeldiagram eller donutdiagram kan eksempelvis anvendes til at vise procentfordelingen.

### Acceptkriterier

**Scenario: Vis månedlige udgifter**

**Given** brugeren har registreret udgifter i den valgte måned<br>
**When** brugeren åbner den månedlige oversigt<br>
**Then** skal systemet vise et diagram, hvor udgifterne er grupperet efter kategori.

**Scenario: Vis procentfordeling**

**Given** brugeren har registreret udgifter i flere kategorier i den valgte måned<br>
**When** diagrammet vises<br>
**Then** skal systemet vise, hvor stor en procentdel hver kategori udgør af månedens samlede udgifter.

**Scenario: Brugeren vælger en anden måned**

**Given** der findes udgifter fra flere forskellige måneder<br>
**When** brugeren vælger en anden måned<br>
**Then** skal diagrammet opdateres, så det kun viser udgifter fra den valgte måned.

---

## Feature 4 – Slet en udgift

Brugeren skal kunne slette en udgift, som eksempelvis er registreret forkert eller ikke længere er relevant.

### Acceptkriterier

**Scenario: Slet en udgift**

**Given** en udgift findes på brugerens liste over udgifter<br>
**When** brugeren vælger at slette udgiften og bekræfter handlingen<br>
**Then** skal udgiften fjernes fra systemet.

**Scenario: Annuller sletning**

**Given** brugeren har valgt at slette en udgift<br>
**When** brugeren annullerer handlingen<br>
**Then** skal udgiften fortsat eksistere uændret i systemet.

---

## Feature 5 – Registrer en fremtidig udgift

Brugeren skal kunne oprette en forventet udgift med en dato i fremtiden.

Dette kan eksempelvis anvendes til:

- abonnementer
- husleje
- forsikring
- medlemskaber
- forventede regninger

En fremtidig udgift betragtes som en planlagt udgift og skal derfor ikke automatisk behandles som en faktisk udgift.

Når datoen for udgiften nås, skal brugeren kunne bekræfte, om betalingen faktisk fandt sted.

### Acceptkriterier

**Scenario: Opret en fremtidig udgift**

**Given** brugeren er ved at oprette en ny udgift<br>
**When** brugeren vælger en dato i fremtiden og gemmer udgiften<br>
**Then** skal udgiften gemmes som en planlagt fremtidig udgift.

**Scenario: En planlagt udgift når sin dato**

**Given** der findes en fremtidig udgift, og den planlagte dato er nået<br>
**When** brugeren åbner applikationen eller den relevante månedsoversigt<br>
**Then** skal systemet bede brugeren om at bekræfte, om udgiften faktisk fandt sted.

**Scenario: Brugeren bekræfter den fremtidige udgift**

**Given** den planlagte dato for en fremtidig udgift er nået<br>
**When** brugeren bekræfter, at udgiften fandt sted<br>
**Then** skal udgiften registreres som en faktisk udgift og inkluderes i månedens samlede udgifter.

**Scenario: Brugeren afviser den fremtidige udgift**

**Given** den planlagte dato for en fremtidig udgift er nået<br>
**When** brugeren angiver, at udgiften ikke fandt sted<br>
**Then** skal udgiften ikke medregnes i månedens faktiske udgifter.

---

# 3. Teknologistak

Den planlagte applikation er en webbaseret løsning.

**Backend**

- Python
- Flask eller FastAPI

Den endelige database, frontend-teknologi, diagram-bibliotek og implementering af AI-funktionen besluttes senere i design- og implementeringsfasen.
