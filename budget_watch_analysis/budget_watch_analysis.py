import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

class BudgetWatchAnalysis:
    """

    """
    def __init__(self, filename):
        assert(type(filename) == str)
        self.filename = Path(filename)
        assert(self.filename.suffix == '.csv')
        assert(self.filename.exists())

        self.data = pd.read_csv(self.filename)
        self.data['date'] = pd.to_datetime(self.data['date_formatted'])
        #self.data['date'] = self.data['date_formatted'].dt.date

    def list_budgets(self):
        print(self.data['budget'].unique())

    def list_entries(self, budget, type='EXPENSE'):
        d = self.data.loc[self.data['budget'] == budget]
        d = d.loc[d['type'] == type].reset_index(drop=True)
        print(d[['date','value']])

    def plot_budget(self, budget, freq='1M',
                    NET=True, EXPENSE=True, REVENUE=True):
        d = self.data.loc[self.data['budget'] == budget]
        #print(d.head())

        full_index = self.data.copy()
        full_index = full_index.loc[full_index['type'] != 'BUDGET']['date']

        expense = d.loc[d['type'] == 'EXPENSE']
        expense = pd.merge(full_index, expense[['date', 'value']],
                           left_index=True, right_index=True,
                           on='date', how='outer')
        expense.fillna(0., inplace=True)
        expense = expense.groupby(
            pd.Grouper(key='date', freq=freq)).sum().reset_index()
        expense['expense'] = expense['value']

        revenue = d.loc[d['type'] == 'REVENUE']
        revenue = pd.merge(full_index, revenue[['date', 'value']],
                           left_index=True, right_index=True,
                           on='date', how='outer')
        revenue.fillna(0., inplace=True)
        revenue = revenue.groupby(
            pd.Grouper(key='date', freq=freq)).sum().reset_index()
        revenue['revenue'] = revenue['value']
        # combine data
        dd = pd.merge(expense[['date', 'expense']],
                      revenue[['date', 'revenue']],
                      on='date', how='outer')
        dd['net expense'] = dd['expense'] - dd['revenue']
        # what to plot
        y = []
        if NET:
            y.append('net expense')
        if EXPENSE:
            y.append('expense')
        if REVENUE:
            y.append('revenue')

        dd['date'] = dd['date'].dt.year
        # plot
        dd.plot(x='date', y=y, kind='bar')
        plt.ylabel('sum [€]')
        plt.title('Budget: {}'.format(budget))
        plt.show()

bw = BudgetWatchAnalysis('test_data/BudgetWatch (14)(1).csv')
bw.plot_budget('Stuff', freq='1y')