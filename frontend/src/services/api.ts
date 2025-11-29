// Symulacja backendu – wszystkie funkcje zwracają docelowy format danych.
// Docelowo podmień implementację na fetch(`${base}/api/...`) bez zmian w komponentach.

export interface Transaction {
    id: string;
    name: string;
    amount: number;
    category: string;
    type: 'income' | 'expense';
    date: string;
}

export interface DashboardSummary {
    incomeDaily: number;
    expenseDaily: number;
    balanceDaily: number;
}

export interface ChartData {
    labels: string[];
    data: number[];
}

export interface ChartsResponse {
    daily: { labels: string[]; income: number[]; expense: number[]; balance: number[] };
    weekly: { labels: string[]; balance: number[] };
    monthly: { labels: string[]; balance: number[] };
    unified: {
        yearly: ChartData;
        halfYearly: ChartData;
        quarterly: ChartData;
        monthly: ChartData;
        weekly: ChartData;
    };
    averages: { avgDailyIncome: number; avgDailyExpense: number };
    ranking: { category: string; amount: number }[];
}

const CATEGORIES_INCOME = ['Pensja', 'Premia', 'Zwrot podatku', 'Sprzedaż'];
const CATEGORIES_EXPENSE = ['Jedzenie', 'Mieszkanie', 'Transport', 'Zdrowie', 'Rozrywka', 'Subskrypcje'];

const DESCRIPTIVE_NAMES_INCOME = ['Wypłata wynagrodzenia', 'Premia kwartalna', 'Zwrot z urzędu skarbowego', 'Sprzedaż starego roweru', 'Odsetki z lokaty'];
const DESCRIPTIVE_NAMES_EXPENSE = ['Zakupy Tesco', 'Wizyta u Dentysty', 'Paliwo Orlen', 'Czynsz za mieszkanie', 'Abonament Netflix', 'Bilet do kina', 'Kawa Starbucks', 'Uber Eats'];

function rand(min: number, max: number): number {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function sample<T>(arr: T[]): T {
    return arr[rand(0, arr.length - 1)];
}

function formatDate(d: Date): string {
    const iso = d.toISOString();
    return iso.slice(0, 10);
}

function lastNDays(n: number): string[] {
    const days: string[] = [];
    const today = new Date();
    for (let i = n - 1; i >= 0; i--) {
        const d = new Date(today);
        d.setDate(today.getDate() - i);
        days.push(formatDate(d));
    }
    return days;
}

// Generator transakcji
function generateTransactions(userId: string, count = 100): Transaction[] {
    const items: Transaction[] = [];
    const today = new Date();
    for (let i = 0; i < count; i++) {
        const isIncome = Math.random() < 0.4; // ~40% przychody, 60% wydatki
        const amount = isIncome ? rand(50, 5000) : rand(10, 300);
        const date = new Date(today);
        date.setDate(today.getDate() - rand(0, 60));
        const category = isIncome ? sample(CATEGORIES_INCOME) : sample(CATEGORIES_EXPENSE);
        const name = isIncome ? sample(DESCRIPTIVE_NAMES_INCOME) : sample(DESCRIPTIVE_NAMES_EXPENSE);

        items.push({
            id: `${userId}-${i}`,
            name: name,
            amount: amount, // Positive amount for both, type distinguishes
            category,
            type: isIncome ? 'income' : 'expense',
            date: formatDate(date),
        });
    }
    // Sort najnowsze najpierw
    items.sort((a, b) => (a.date < b.date ? 1 : -1));
    return items;
}

// Cache po użytkowniku
const CACHE = new Map<string, { transactions: Transaction[] }>();

function ensureUserData(userId: string) {
    if (!CACHE.has(userId)) {
        const tx = generateTransactions(userId, 150);
        CACHE.set(userId, { transactions: tx });
    }
    return CACHE.get(userId)!;
}

// DASHBOARD SUMMARY
export async function getDashboardSummary(userId: string): Promise<DashboardSummary> {
    const { transactions } = ensureUserData(userId);
    const today = formatDate(new Date());
    const todayTx = transactions.filter(t => t.date === today);
    const income = todayTx.filter(t => t.type === 'income').reduce((s, t) => s + t.amount, 0);
    const expense = todayTx.filter(t => t.type === 'expense').reduce((s, t) => s + t.amount, 0);
    const balance = income - expense;

    return {
        incomeDaily: income,
        expenseDaily: expense,
        balanceDaily: balance
    };
}

// RECENT TRANSACTIONS (5 najnowsze)
export async function getRecentTransactions(userId: string): Promise<Transaction[]> {
    const { transactions } = ensureUserData(userId);
    return transactions.slice(0, 5);
}

// ALL TRANSACTIONS + FILTERS
export async function getAllTransactions(userId: string, filters: any = {}): Promise<{ items: Transaction[], meta: { total: number } }> {
    const { transactions } = ensureUserData(userId);
    const {
        dateFrom,
        dateTo,
        name,
        amount,
        category,
        type, // 'income' | 'expense' | undefined
    } = filters;

    let out = [...transactions];
    if (dateFrom) out = out.filter(t => t.date >= dateFrom);
    if (dateTo) out = out.filter(t => t.date <= dateTo);
    if (name) out = out.filter(t => t.name.toLowerCase().includes(String(name).toLowerCase()));
    if (typeof amount === 'number') out = out.filter(t => t.amount === amount);
    if (category) out = out.filter(t => t.category === category);
    if (type) out = out.filter(t => t.type === type);

    return {
        items: out,
        meta: {
            total: out.length
        }
    };
}

// CHARTS DATA
export async function getCharts(userId: string): Promise<ChartsResponse> {
    // Ostatnie 30 dni – słupki przychodów i wydatków
    const days = lastNDays(30);
    const dailyIncome = days.map(() => rand(0, 400));
    const dailyExpense = days.map(() => rand(0, 350));

    // Bilans dzienny
    const dailyBalance = days.map((_, i) => dailyIncome[i] - dailyExpense[i]);

    // Tygodniowy (ostatnie 12 tyg.)
    const weeks = Array.from({ length: 12 }, (_, i) => `T-${12 - i}`);
    const weeklyBalance = weeks.map(() => rand(-800, 1200));

    // Miesięczny (ostatnie 12 mies.)
    const months = Array.from({ length: 12 }, (_, i) => `M-${12 - i}`);
    const monthlyBalance = months.map(() => rand(-2500, 4500));

    // Unified Balance Chart Data
    const yearlyLabels = Array.from({ length: 12 }, (_, i) => `Month ${i + 1}`);
    const yearlyData = yearlyLabels.map(() => rand(-5000, 8000));

    const halfYearlyLabels = Array.from({ length: 6 }, (_, i) => `Month ${i + 1}`);
    const halfYearlyData = halfYearlyLabels.map(() => rand(-4000, 6000));

    const quarterlyLabels = Array.from({ length: 3 }, (_, i) => `Month ${i + 1}`);
    const quarterlyData = quarterlyLabels.map(() => rand(-3000, 5000));

    const monthlyLabels = lastNDays(30);
    const monthlyData = monthlyLabels.map(() => rand(-500, 800));

    const weeklyLabels = lastNDays(7);
    const weeklyData = weeklyLabels.map(() => rand(-200, 400));


    // Średnie wartości dzienne (linia) - Last Month
    const avgDailyIncome = Math.round(dailyIncome.reduce((a, b) => a + b, 0) / dailyIncome.length);
    const avgDailyExpense = Math.round(dailyExpense.reduce((a, b) => a + b, 0) / dailyExpense.length);

    // Ranking kategorii (ostatnie 3 mies.) – wydatki
    const rankingCategories = CATEGORIES_EXPENSE.map(cat => ({
        category: cat,
        amount: rand(300, 2000)
    })).sort((a, b) => b.amount - a.amount);

    return {
        daily: { labels: days, income: dailyIncome, expense: dailyExpense, balance: dailyBalance },
        weekly: { labels: weeks, balance: weeklyBalance },
        monthly: { labels: months, balance: monthlyBalance },
        unified: {
            yearly: { labels: yearlyLabels, data: yearlyData },
            halfYearly: { labels: halfYearlyLabels, data: halfYearlyData },
            quarterly: { labels: quarterlyLabels, data: quarterlyData },
            monthly: { labels: monthlyLabels, data: monthlyData },
            weekly: { labels: weeklyLabels, data: weeklyData },
        },
        averages: { avgDailyIncome, avgDailyExpense },
        ranking: rankingCategories
    };
}

export const meta = {
    categories: {
        income: CATEGORIES_INCOME,
        expense: CATEGORIES_EXPENSE
    }
};
