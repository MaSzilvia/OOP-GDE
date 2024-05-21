from abc import ABC, abstractmethod
import datetime as dt


class Szoba(ABC):
    def __init__(self, szam: int, ar: int):
        self.szam = szam
        self.ar = ar

    @abstractmethod
    def agyakszama(self):
        pass

    def __str__(self):
        return "Szobaszam: " + str(self.szam) + ", szoba ára egy napra: " + str(self.ar)


class EgyagyasSzoba(Szoba):
    def agyakszama(self):
        return 1


class KetagyasSzoba(Szoba):
    def agyakszama(self):
        return 2


def is_date_overlap(elso_eleje: dt, elso_vege: dt, masodik_eleje: dt, masodik_vege: dt):
    return (elso_eleje <= masodik_vege) and (masodik_eleje <= elso_vege)


class Foglalas:
    def __init__(self, startdate: dt, enddate: dt, szoba: Szoba):
        self.startdate = startdate
        self.enddate = enddate
        self.szoba = szoba

    def __str__(self):
        return ("szoba szama: " + str(self.szoba.szam) + " foglalás kezdete: " + self.startdate.isoformat() +
                ' foglalás vége: ' + self.enddate.isoformat() +
                " foglalás ára: " + str((self.enddate - self.startdate).days * self.szoba.ar))


class Szalloda:
    def __init__(self, nev):
        self.nev = nev
        self.szobak: list[Szoba] = []
        self.foglalasok: list[Foglalas] = []

    def get_szoba_by_number(self, szobaszam):
        for szoba in self.szobak:
            if szoba.szam == szobaszam:
                return szoba
        return None

    def add_foglalas(self, startdate, enddate, szoba):
        self.foglalasok.append(Foglalas(startdate, enddate, szoba))
        return (enddate - startdate).days * szoba.ar

    def check_foglalas(self, startdate: dt, enddate: dt, szoba):
        if (startdate > enddate):
            raise ValueError("A foglalás kezdete korábban kell legyen, mint a vége")
        if startdate <= dt.date.today():
            raise ValueError("A foglalásnak legkorábban holnap szabad kezdődnie")
        for foglalas in self.foglalasok:
            if (foglalas.szoba.szam == szoba.szam and
                    is_date_overlap(foglalas.startdate, foglalas.enddate, startdate, enddate)):
                raise ValueError("A foglalás ütközik egy már meglévő foglalással: " + str(foglalas))

    def remove_foglalas(self, foglalas):
        self.foglalasok.remove(foglalas)

    def list_foglalas(self):
        strings = []
        for i in range(len(self.foglalasok)):
            strings.append(str(i + 1) + ". foglalás: " + str(self.foglalasok[i]))
        return '\n'.join(strings)

    def list_szoba(self):
        strings = []
        for i in range(len(self.szobak)):
            strings.append(str(i + 1) + ". szoba: " + str(self.szobak[i]))
        return '\n'.join(strings)


def input_with_exit(msg):
    str = input(msg)
    if str == "exit":
        exit(0)
    return str


def get_user_input_int(user_msg: str):
    while True:
        try:
            return int(input_with_exit(user_msg))
        except ValueError:
            print("Kérem számot írjon be")


def get_user_input_in_range(lower, upper):
    while True:
        num = get_user_input_int("Írjon be egy számot " + str(lower) + " és " + str(upper) + " között: ")
        if num < lower or num > upper:
            print("Rossz számot írt be")
            continue
        return num


def gen_init_data():
    szalloda = Szalloda("vacak")
    egyagyas = EgyagyasSzoba(1, 200)
    ketagyas = KetagyasSzoba(2, 450)
    egyagyas_2 = EgyagyasSzoba(33, 666)
    szalloda.szobak.append(egyagyas)
    szalloda.szobak.append(ketagyas)
    szalloda.szobak.append(egyagyas_2)
    szalloda.add_foglalas(dt.date.today(), dt.date.today() + dt.timedelta(days=1), egyagyas)
    szalloda.add_foglalas(dt.date.today(), dt.date.today() + dt.timedelta(days=5), ketagyas)
    szalloda.add_foglalas(dt.date.today() + dt.timedelta(days=5), dt.date.today() + dt.timedelta(days=6), egyagyas_2)
    szalloda.add_foglalas(dt.date.today() + dt.timedelta(days=2), dt.date.today() + dt.timedelta(days=3), egyagyas_2)
    szalloda.add_foglalas(dt.date.today() + dt.timedelta(days=7), dt.date.today() + dt.timedelta(days=15), egyagyas_2)
    return szalloda


def get_date_from_user():
    while True:
        try:
            date_input = input_with_exit("Írja be a dátumot ÉÉÉÉ-HH-NN formátumban: ")
            return dt.datetime.strptime(date_input, "%Y-%m-%d").date()
        except ValueError:
            print("Hibás dátum formátum")


def handle_create_foglalas(szalloda):
    print("A szálloda szobái:")
    print(szalloda.list_szoba())
    print("A foglalások:")
    print(szalloda.list_foglalas())
    szoba = get_szoba_with_user_input(szalloda)
    print("Kérem a foglalás kezdetét:")
    start = get_date_from_user()
    print("Kérem a foglalás végét:")
    end = get_date_from_user()
    try:
        szalloda.check_foglalas(start, end, szoba)
        szalloda.add_foglalas(start, end, szoba)
        print(szalloda.list_foglalas())
    except ValueError as er:
        print(er)


def get_szoba_with_user_input(szalloda):
    while True:
        szobaszam = get_user_input_int("Kérem a szoba számát, amelyiket szeretné lefoglalni: ")
        szoba = szalloda.get_szoba_by_number(szobaszam)
        if szoba is None:
            print("Nincs ilyen szobaszam")
            continue
        return szoba


def handle_delete_foglalas(szalloda):
    print("A jelenlegi foglalások:")
    print(szalloda.list_foglalas())
    print("Hányas számú foglalást szeretné lemondani?")
    user_choice = get_user_input_in_range(1, len(szalloda.foglalasok))
    print("Biztosan törölni szeretné ezt a foglalást? " + str(szalloda.foglalasok[user_choice - 1]))
    print("1: igen, 2: nem")
    user_choice = get_user_input_in_range(1, 2)
    if user_choice == 1:
        del (szalloda.foglalasok[user_choice - 1])
        print("Foglalás sikeresen törölve, megmaradó foglalások:")
        print(szalloda.list_foglalas())


szalloda = gen_init_data()

print("Üdvüzli a " + szalloda.nev + " szálloda programja")
print("A programból bármikor kiléphet az exit szó beírásával")
while True:
    print("Válasszon egyet az alábbi opciók közül:")
    print("1: új foglalás\n2: foglalás lemondása\n"
          "3: létező foglalások listázása\negyéb szám: kilépés a programból: ")

    user_choice = get_user_input_int("")
    match user_choice:
        case 1:
            handle_create_foglalas(szalloda)
        case 2:
            handle_delete_foglalas(szalloda)
        case 3:
            print(szalloda.list_foglalas())
        case _:
            exit(0)
