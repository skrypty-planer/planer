const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

export interface DashboardSummary {
    incomeDaily: number;
    expenseDaily: number;
    balanceDaily: number;
    incomeMonthly: number;
    expenseMonthly: number;
    balanceMonthly: number;
}

export interface Transaction {
    id: string;
    name: string;
    amount: number;
    date: string;
    type: 'income' | 'expense';
    category: string;
}

export interface TransactionFilter {
    dateFrom?: string;
    dateTo?: string;
    name?: string;
    amount?: number; // Not commonly used in this UI but supported
    amountMin?: number; // Backend uses these
    amountMax?: number;
    category?: string;
    type?: 'income' | 'expense' | '';
    sort?: string;
}

export interface CategoryBreakdown {
    category: string;
    amount: number;
    percentage: number;
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

export const meta = {
    categories: {
        income: ['Pensja', 'Premia', 'Zwrot podatku', 'Sprzedaż'],
        expense: ['Jedzenie', 'Mieszkanie', 'Transport', 'Zdrowie', 'Rozrywka', 'Subskrypcje']
    }
};

async function request(endpoint: string, options: RequestInit = {}) {
    const res = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
        credentials: 'include'
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
        throw new Error(data.message || 'Request failed');
    }

    return data;
}

// DASHBOARD SUMMARY
export async function getDashboardSummary(userId: string): Promise<DashboardSummary> {
    const res = await request(`/transactions/summary?user_id=${userId}`);
    return res.summary;
}

// RECENT TRANSACTIONS (5)
export async function getRecentTransactions(userId: string): Promise<Transaction[]> {
    const res = await request(`/transactions/recent?user_id=${userId}`);
    return res.transactions;
}

// ALL TRANSACTIONS + FILTERS
export async function getAllTransactions(userId: string, filters: TransactionFilter = {}): Promise<{ items: Transaction[], meta: { total: number } }> {
    const params = new URLSearchParams();
    params.append('user_id', userId);

    if (filters.dateFrom) params.append('dateFrom', filters.dateFrom);
    if (filters.dateTo) params.append('dateTo', filters.dateTo);
    if (filters.name) params.append('name', filters.name);
    if (filters.category) params.append('category', filters.category);
    // Support frontend 'amount' or backend 'amountMin/Max'
    if (filters.amountMin !== undefined) params.append('amountMin', filters.amountMin.toString());
    if (filters.amountMax !== undefined) params.append('amountMax', filters.amountMax.toString());

    if (filters.type) params.append('type', filters.type);
    if (filters.sort) params.append('sort', filters.sort);

    const res = await request(`/transactions/get?${params.toString()}`);
    return res;
}

export async function getCharts(userId: string): Promise<ChartsResponse> {
    const res = await request(`/transactions/charts?user_id=${userId}`);
    return res.charts;
}

// ADD TRANSACTION
export async function addTransaction(userId: string, transaction: Omit<Transaction, 'id'>): Promise<Transaction> {
    const res = await request('/transactions/store', {
        method: 'POST',
        body: JSON.stringify({ ...transaction, user_id: userId }) // Backend handles session but we can pass ID too
    });
    return res.transaction;
}

// UPDATE TRANSACTION
export async function updateTransaction(userId: string, transactionId: string, updates: Partial<Transaction>): Promise<Transaction | null> {
    const res = await request(`/transactions/update/${transactionId}`, {
        method: 'PUT',
        body: JSON.stringify({ ...updates, user_id: userId })
    });
    return res.transaction;
}

// DELETE TRANSACTION
export async function deleteTransaction(userId: string, transactionId: string): Promise<boolean> {
    try {
        const res = await request(`/transactions/delete/${transactionId}?user_id=${userId}`, {
            method: 'DELETE'
        });
        return res.success;
    } catch {
        return false;
    }
}

// CATEGORY BREAKDOWN
export async function getCategoryBreakdown(
    userId: string,
    type: 'income' | 'expense',
    period: 'yearly' | 'halfYearly' | 'quarterly' | 'monthly' | 'weekly'
): Promise<CategoryBreakdown[]> {
    const res = await request(`/transactions/categories?user_id=${userId}&type=${type}&period=${period}`);
    return res.breakdown;
}
