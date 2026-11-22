import random
from django.shortcuts import render, redirect
from appcom.models import Partida

SALDO_INICIAL = 1000
APUESTAS_VALIDAS = [10, 20, 30, 50]

RANGOS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
PALOS = ['♠', '♥', '♦', '♣']


def carta():
    return {'rango': random.choice(RANGOS), 'palo': random.choice(PALOS)}


def valor(c):
    if c['rango'] == 'A':
        return 11
    if c['rango'] in ('J', 'Q', 'K'):
        return 10
    return int(c['rango'])


def suma(mano):
    total = sum(valor(c) for c in mano)
    ases = sum(1 for c in mano if c['rango'] == 'A')
    # Cada As pasa de valer 11 a valer 1 si te pasarías de 21
    while total > 21 and ases:
        total -= 10
        ases -= 1
    return total


def nueva_partida(request):
    # Deja la mesa lista para apostar. Las cartas se reparten al apostar.
    request.session['jugador'] = []
    request.session['dealer'] = []
    request.session['apuesta'] = 0
    request.session['terminada'] = False
    request.session['mensaje'] = ''
    saldo = request.session.get('saldo', SALDO_INICIAL)
    if saldo < min(APUESTAS_VALIDAS):
        saldo = SALDO_INICIAL  # sin dinero para apostar: se reinicia el crédito
    request.session['saldo'] = saldo


def terminar(request):
    jugador = request.session['jugador']
    dealer = request.session['dealer']
    apuesta = request.session.get('apuesta', 0)

    # el dealer solo juega si el jugador no se pasó
    if suma(jugador) <= 21:
        while suma(dealer) < 17:
            dealer.append(carta())

    if suma(jugador) > 21:
        mensaje, resultado = "Te pasaste de 21, perdiste", "pierde"
    elif suma(dealer) > 21:
        mensaje, resultado = "El dealer se pasó, ganaste", "gana"
    elif suma(jugador) > suma(dealer):
        mensaje, resultado = "Ganaste", "gana"
    elif suma(jugador) < suma(dealer):
        mensaje, resultado = "Perdiste", "pierde"
    else:
        mensaje, resultado = "Empate", "empate"

    # La apuesta ya se descontó al apostar: si ganas te devuelven el doble,
    # si empatas te devuelven lo apostado y si pierdes no recuperas nada.
    saldo = request.session.get('saldo', 0)
    if resultado == "gana":
        saldo += apuesta * 2
    elif resultado == "empate":
        saldo += apuesta
    request.session['saldo'] = saldo

    # Historial: solo se guardan las 2 últimas partidas (la más reciente arriba)
    historial = request.session.get('historial', [])
    cantidad_historial = apuesta * 2 if resultado == "gana" else apuesta
    historial.insert(0, {'tipo': resultado, 'cantidad': cantidad_historial})
    request.session['historial'] = historial[:2]

    # Guardar la partida en la base de datos (solo si hay un usuario con sesión)
    if request.user.is_authenticated:
        Partida.objects.create(
            usuario=request.user,
            apuesta=apuesta,
            puntos=suma(jugador),
            resultado=resultado,
        )

    request.session['dealer'] = dealer      # reasignamos para que Django guarde el cambio
    request.session['terminada'] = True
    request.session['mensaje'] = mensaje


def inicio(request):
    # Si la sesión viene de la versión anterior (cartas como números), se reinicia la mesa
    mano_vieja = any(
        not isinstance(c, dict)
        for c in request.session.get('jugador', []) + request.session.get('dealer', [])
    )
    if 'jugador' not in request.session or mano_vieja:
        nueva_partida(request)

    jugador = request.session['jugador']
    dealer = request.session['dealer']
    apuesta = request.session.get('apuesta', 0)
    contexto = {
        'jugador': jugador,
        'suma_jugador': suma(jugador),
        'dealer': dealer,
        'suma_dealer': suma(dealer),
        'terminada': request.session['terminada'],
        'mensaje': request.session['mensaje'],
        'saldo': request.session.get('saldo', SALDO_INICIAL),
        'apuesta': apuesta,
        'posible_ganancia': apuesta * 2,
        'apostando': apuesta == 0,
        'apuestas': APUESTAS_VALIDAS,
        'historial': request.session.get('historial', []),
    }
    return render(request, 'core/blackjack.html', contexto)


def apostar(request):
    if request.method == 'POST' and request.session.get('apuesta', 0) == 0:
        try:
            cantidad = int(request.POST.get('cantidad', 0))
        except ValueError:
            cantidad = 0
        saldo = request.session.get('saldo', SALDO_INICIAL)
        if cantidad in APUESTAS_VALIDAS and cantidad <= saldo:
            request.session['saldo'] = saldo - cantidad
            request.session['apuesta'] = cantidad
            request.session['jugador'] = [carta(), carta()]
            request.session['dealer'] = [carta(), carta()]
            request.session['terminada'] = False
            request.session['mensaje'] = ''
    return redirect('inicio')


def pedir(request):
    if (request.method == 'POST'
            and not request.session.get('terminada')
            and request.session.get('apuesta', 0) > 0):
        jugador = request.session['jugador']
        jugador.append(carta())
        request.session['jugador'] = jugador
        if suma(jugador) >= 21:
            terminar(request)
    return redirect('inicio')


def plantarse(request):
    if (request.method == 'POST'
            and not request.session.get('terminada')
            and request.session.get('apuesta', 0) > 0):
        terminar(request)
    return redirect('inicio')


def nueva(request):
    if request.method == 'POST':
        nueva_partida(request)
    return redirect('inicio')