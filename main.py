import random
import time

# ─── Lista externa de especies ────────────────────────────────────────────────
ESPECIES = [
    {"nome": "Tambaqui",  "peso_min": 1.0,  "peso_max": 30.0},
    {"nome": "Pacu",      "peso_min": 0.5,  "peso_max": 20.0},
    {"nome": "Pirarucu",  "peso_min": 5.0,  "peso_max": 50.0},
    {"nome": "Tilapia",   "peso_min": 0.3,  "peso_max": 5.0 },
    {"nome": "Tucunare",  "peso_min": 0.5,  "peso_max": 8.0 },
    {"nome": "Piranha",   "peso_min": 0.2,  "peso_max": 3.0 },
    {"nome": "Dourado",   "peso_min": 2.0,  "peso_max": 25.0},
]

# ─── Estruturas ───────────────────────────────────────────────────────────────

class Peixe:
    def __init__(self, id_peixe, especie, peso):
        self.id_peixe = id_peixe
        self.especie  = especie
        self.peso     = peso
        self.proximo  = None

    def __str__(self):
        return f"[{self.especie} | ID:{self.id_peixe} | {self.peso}kg]"


class Mochila:
    def __init__(self, slots=10):
        self.slots         = slots
        self.tabela        = [None] * self.slots
        self.total_pescado = 0
        self._ids          = set()          # rastreia IDs para evitar duplicatas

    # ── hash ──────────────────────────────────────────────────────────────────
    def _hash(self, id_peixe):
        return id_peixe % self.slots

    # ── inserção com checagem de duplicata ────────────────────────────────────
    def guardar(self, peixe):
        if peixe.id_peixe in self._ids:
            print(f"  Aviso: peixe ID {peixe.id_peixe} ja esta na mochila. Descartado.")
            return False

        indice = self._hash(peixe.id_peixe)

        if self.tabela[indice] is None:
            self.tabela[indice] = peixe
        else:
            # tratamento de colisao: percorre a chain ate o fim
            atual = self.tabela[indice]
            while atual.proximo:
                atual = atual.proximo
            atual.proximo = peixe

        self._ids.add(peixe.id_peixe)
        self.total_pescado += 1
        return True

    # ── busca por ID ──────────────────────────────────────────────────────────
    def buscar(self, id_peixe):
        indice = self._hash(id_peixe)
        atual  = self.tabela[indice]
        passos = 0
        while atual:
            passos += 1
            if atual.id_peixe == id_peixe:
                return atual, indice, passos
            atual = atual.proximo
        return None, indice, passos

    # ── busca linear (sem hash) — para comparação ─────────────────────────────
    def buscar_linear(self, id_peixe):
        """Percorre todos os slots/chains sem usar a hash. Simula busca sequencial."""
        passos = 0
        for i in range(self.slots):
            atual = self.tabela[i]
            while atual:
                passos += 1
                if atual.id_peixe == id_peixe:
                    return atual, passos
                atual = atual.proximo
        return None, passos

    # ── remover por ID ────────────────────────────────────────────────────────
    def remover(self, id_peixe):
        indice   = self._hash(id_peixe)
        atual    = self.tabela[indice]
        anterior = None

        while atual:
            if atual.id_peixe == id_peixe:
                if anterior:
                    anterior.proximo = atual.proximo
                else:
                    self.tabela[indice] = atual.proximo
                self._ids.discard(id_peixe)
                self.total_pescado -= 1
                return True
            anterior = atual
            atual    = atual.proximo
        return False

    # ── listagem ──────────────────────────────────────────────────────────────
    def listar_conteudo(self):
        print(f"\n--- Mochila ({self.total_pescado} peixes | {self.slots} slots) ---")
        for i in range(self.slots):
            if self.tabela[i]:
                chain = []
                atual = self.tabela[i]
                while atual:
                    chain.append(str(atual))
                    atual = atual.proximo
                colisoes = f"  ({len(chain)-1} colisao)" if len(chain) > 1 else ""
                print(f"  Slot {i:>2}: {' -> '.join(chain)}{colisoes}")
            else:
                print(f"  Slot {i:>2}: vazio")

    # ── estatísticas ──────────────────────────────────────────────────────────
    def estatisticas(self):
        chains    = []
        ocupados  = 0
        for i in range(self.slots):
            tam = 0
            atual = self.tabela[i]
            while atual:
                tam  += 1
                atual = atual.proximo
            chains.append(tam)
            if tam > 0:
                ocupados += 1

        maior   = max(chains)
        fator   = self.total_pescado / self.slots
        colisoes = sum(1 for c in chains if c > 1)

        print(f"\n  Slots ocupados : {ocupados}/{self.slots}")
        print(f"  Fator de carga : {fator:.2f}")
        print(f"  Maior chain    : {maior}")
        print(f"  Slots c/ colisao: {colisoes}")

# ─── Helpers ──────────────────────────────────────────────────────────────────

def gerar_id():
    return random.randint(10000, 99999)

def gerar_peixe():
    especie_data = random.choice(ESPECIES)
    nome  = especie_data["nome"]
    peso  = round(random.uniform(especie_data["peso_min"], especie_data["peso_max"]), 2)
    return Peixe(gerar_id(), nome, peso)

# ─── Ações do jogo ────────────────────────────────────────────────────────────

def pescar_um_peixe(mochila):
    print("\nJogando a linha...")
    p = gerar_peixe()
    print(f"  Fisgou: {p.especie} ({p.peso}kg) | ID: {p.id_peixe}")
    if input("  Deseja guardar? (s/n): ").strip().lower() == 's':
        if mochila.guardar(p):
            slot = mochila._hash(p.id_peixe)
            print(f"  Guardado no slot {slot}.")


def pesca_em_massa(mochila, quantidade=50):
    print(f"\nPescando com rede ({quantidade} tentativas)...")
    guardados = 0
    for _ in range(quantidade):
        p = gerar_peixe()
        if mochila.guardar(p):
            guardados += 1
    print(f"  {guardados} peixes novos guardados.")


def buscar_peixe(mochila):
    try:
        bid = int(input("  ID do peixe: ").strip())
    except ValueError:
        print("  ID invalido.")
        return

    peixe, slot, passos = mochila.buscar(bid)
    if peixe:
        print(f"  Encontrado no slot {slot} ({passos} passo(s)): {peixe}")
    else:
        print(f"  Nao encontrado. Verificado slot {slot} em {passos} passo(s).")


def soltar_peixe(mochila):
    try:
        bid = int(input("  ID do peixe a soltar: ").strip())
    except ValueError:
        print("  ID invalido.")
        return

    if mochila.remover(bid):
        print(f"  Peixe ID {bid} solto de volta ao rio.")
    else:
        print(f"  Peixe ID {bid} nao encontrado na mochila.")


def listar_especies():
    print("\n--- Especies disponíveis ---")
    for e in ESPECIES:
        print(f"  {e['nome']:<12} | {e['peso_min']}kg – {e['peso_max']}kg")


def benchmark(mochila, amostras=200):
    """Compara tempo médio de busca com hash vs busca linear (sem hash)."""
    if mochila.total_pescado == 0:
        print("\n  Mochila vazia. Adicione peixes primeiro.")
        return

    ids_existentes = list(mochila._ids)
    # usa no máximo `amostras` IDs reais para buscar
    ids_teste = random.sample(ids_existentes, min(amostras, len(ids_existentes)))

    # ── busca COM hash ────────────────────────────────────────────────────────
    t0 = time.perf_counter()
    passos_hash = []
    for bid in ids_teste:
        _, _, p = mochila.buscar(bid)
        passos_hash.append(p)
    t_hash = (time.perf_counter() - t0) / len(ids_teste)

    # ── busca SEM hash (linear) ───────────────────────────────────────────────
    t0 = time.perf_counter()
    passos_linear = []
    for bid in ids_teste:
        _, p = mochila.buscar_linear(bid)
        passos_linear.append(p)
    t_linear = (time.perf_counter() - t0) / len(ids_teste)

    ganho = t_linear / t_hash if t_hash > 0 else float('inf')

    print(f"\n{'='*42}")
    print(f"  BENCHMARK — {len(ids_teste)} buscas de IDs existentes")
    print(f"{'='*42}")
    print(f"  {'':25} {'COM hash':>10}  {'SEM hash':>10}")
    print(f"  {'-'*47}")
    print(f"  {'Tempo médio por busca':25} {t_hash*1e6:>9.2f}µs  {t_linear*1e6:>9.2f}µs")
    print(f"  {'Passos médios':25} {sum(passos_hash)/len(passos_hash):>10.2f}  {sum(passos_linear)/len(passos_linear):>10.2f}")
    print(f"  {'Passos máximos':25} {max(passos_hash):>10}  {max(passos_linear):>10}")
    print(f"{'='*42}")
    print(f"  Hash foi {ganho:.1f}x mais rapido que busca linear.")
    print(f"{'='*42}")

# ─── Loop principal ───────────────────────────────────────────────────────────

def mini_game():
    try:
        s = int(input("Quantos slots para a mochila? (padrao 100): ").strip() or "100")
    except ValueError:
        s = 100
    mochila = Mochila(slots=max(1, s))

    # ── pré-carrega 995 peixes para atender o requisito mínimo ───────────────
    print("\nCarregando base de dados (995 peixes)...")
    tentativas = 0
    while mochila.total_pescado < 995 and tentativas < 5000:
        p = gerar_peixe()
        mochila.guardar(p)
        tentativas += 1
    print(f"  {mochila.total_pescado} peixes carregados na mochila.")

    while True:
        print("\n" + "=" * 36)
        print(f"  Mochila: {mochila.total_pescado} peixes | {mochila.slots} slots")
        print("  [1] Pescar um peixe")
        print("  [2] Pescar com rede")
        print("  [3] Ver mochila")
        print("  [4] Buscar peixe por ID")
        print("  [5] Soltar peixe por ID")
        print("  [6] Estatísticas da mochila")
        print("  [7] Ver especies")
        print("  [8] Benchmark (hash vs linear)")
        print("  [9] Sair")

        opcao = input("  Escolha: ").strip()

        if   opcao == '1': pescar_um_peixe(mochila)
        elif opcao == '2':
            try:
                q = int(input("  Quantos peixes? (padrao 50): ").strip() or "50")
            except ValueError:
                q = 50
            pesca_em_massa(mochila, q)
        elif opcao == '3': mochila.listar_conteudo()
        elif opcao == '4': buscar_peixe(mochila)
        elif opcao == '5': soltar_peixe(mochila)
        elif opcao == '6': mochila.estatisticas()
        elif opcao == '7': listar_especies()
        elif opcao == '8': benchmark(mochila)
        elif opcao == '9': print("Ate logo!"); break
        else: print("  Opcao invalida.")


if __name__ == "__main__":
    mini_game()
