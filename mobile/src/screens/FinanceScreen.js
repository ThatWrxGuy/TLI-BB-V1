import React, { useState, useEffect } from 'react'
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, RefreshControl, FlatList } from 'react-native'
import { financeAPI } from '../services/api'

export default function FinanceScreen() {
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [accounts, setAccounts] = useState([])
  const [insights, setInsights] = useState(null)
  const [transactions, setTransactions] = useState([])

  useEffect(() => {
    loadFinance()
  }, [])

  const loadFinance = async () => {
    try {
      const [accountsRes, insightsRes, transRes] = await Promise.all([
        financeAPI.getAccounts(),
        financeAPI.getInsights(30),
        financeAPI.getTransactions({ limit: 10 })
      ])
      setAccounts(accountsRes.data.accounts || [])
      setInsights(insightsRes.data)
      setTransactions(transRes.data.transactions || [])
    } catch (err) {
      console.error('Failed to load finance:', err)
    } finally {
      setLoading(false)
    }
  }

  const onRefresh = async () => {
    setRefreshing(true)
    await loadFinance()
    setRefreshing(false)
  }

  const formatCurrency = (amount) => {
    return `$${Number(amount || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}`
  }

  const TransactionItem = ({ tx }) => (
    <View style={styles.transactionItem}>
      <View style={styles.transactionLeft}>
        <View style={[styles.transactionIcon, { backgroundColor: '#FEF3C7' }]}>
          <Text style={styles.transactionIconText}>💳</Text>
        </View>
        <View>
          <Text style={styles.transactionName}>{tx.merchant_name || tx.name}</Text>
          <Text style={styles.transactionCategory}>{tx.category}</Text>
        </View>
      </View>
      <Text style={[styles.transactionAmount, tx.amount < 0 ? styles.amountNegative : styles.amountPositive]}>
        {tx.amount < 0 ? '-' : '+'}{formatCurrency(Math.abs(tx.amount))}
      </Text>
    </View>
  )

  const CategoryItem = ({ category, amount, percentage, icon }) => (
    <View style={styles.categoryItem}>
      <View style={styles.categoryLeft}>
        <Text style={styles.categoryIcon}>{icon}</Text>
        <Text style={styles.categoryName}>{category}</Text>
      </View>
      <View style={styles.categoryRight}>
        <Text style={styles.categoryAmount}>{formatCurrency(amount)}</Text>
        <Text style={styles.categoryPercent}>{percentage}%</Text>
      </View>
    </View>
  )

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    )
  }

  return (
    <View style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Finance</Text>
          <TouchableOpacity style={styles.addButton}>
            <Text style={styles.addButtonText}>+ Link</Text>
          </TouchableOpacity>
        </View>

        {/* Net Worth Card */}
        <View style={styles.netWorthCard}>
          <View>
            <Text style={styles.netWorthLabel}>Net Worth</Text>
            <Text style={styles.netWorthValue}>{formatCurrency(insights?.net_worth)}</Text>
            <View style={styles.netWorthTrend}>
              <Text style={styles.trendPositive}>↑ 3.2%</Text>
              <Text style={styles.trendText}>this month</Text>
            </View>
          </View>
          <View style={styles.netWorthIcon}>
            <Text style={{ fontSize: 40 }}>💰</Text>
          </View>
        </View>

        {/* Quick Stats */}
        <View style={styles.statsRow}>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>Income</Text>
            <Text style={[styles.statValue, styles.incomeValue]}>{formatCurrency(insights?.total_income)}</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>Spending</Text>
            <Text style={[styles.statValue, styles.spendingValue]}>{formatCurrency(insights?.total_spending)}</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>Net</Text>
            <Text style={[styles.statValue, styles.netValue]}>{formatCurrency(insights?.net_flow)}</Text>
          </View>
        </View>

        {/* Spending by Category */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Spending by Category</Text>
          <View style={styles.categoryList}>
            {insights?.spending_by_category?.map((cat, i) => (
              <CategoryItem 
                key={cat.category} 
                category={cat.category} 
                amount={cat.amount} 
                percentage={cat.percentage}
                icon={cat.icon || '📦'}
              />
            ))}
          </View>
        </View>

        {/* Recent Transactions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recent Transactions</Text>
          <View style={styles.transactionList}>
            {transactions.map((tx) => (
              <TransactionItem key={tx.id} tx={tx} />
            ))}
          </View>
        </View>

        {/* Insights */}
        {insights?.insights?.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Insights</Text>
            <View style={styles.insightsList}>
              {insights.insights.map((insight, i) => (
                <View key={i} style={styles.insightItem}>
                  <Text style={styles.insightText}>💡 {insight}</Text>
                </View>
              ))}
            </View>
          </View>
        )}

        <View style={styles.bottomPadding} />
      </ScrollView>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FAFAF9',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: '#6B7280',
  },
  scrollView: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 16,
    paddingBottom: 12,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1C1917',
  },
  addButton: {
    backgroundColor: '#F59E0B',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  addButtonText: {
    color: '#FFFFFF',
    fontWeight: '600',
    fontSize: 14,
  },
  netWorthCard: {
    backgroundColor: '#F59E0B',
    marginHorizontal: 20,
    borderRadius: 20,
    padding: 24,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  netWorthLabel: {
    color: 'rgba(255,255,255,0.8)',
    fontSize: 14,
  },
  netWorthValue: {
    color: '#FFFFFF',
    fontSize: 36,
    fontWeight: 'bold',
    marginVertical: 4,
  },
  netWorthTrend: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  trendPositive: {
    color: '#FFFFFF',
    fontWeight: '600',
    fontSize: 14,
  },
  trendText: {
    color: 'rgba(255,255,255,0.8)',
    fontSize: 14,
    marginLeft: 4,
  },
  netWorthIcon: {
    width: 70,
    height: 70,
    backgroundColor: 'rgba(255,255,255,0.2)',
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  statsRow: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    marginBottom: 20,
  },
  statBox: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    marginHorizontal: 4,
    alignItems: 'center',
  },
  statLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginBottom: 4,
  },
  statValue: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  incomeValue: {
    color: '#10B981',
  },
  spendingValue: {
    color: '#EF4444',
  },
  netValue: {
    color: '#3B82F6',
  },
  section: {
    paddingHorizontal: 20,
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1C1917',
    marginBottom: 12,
  },
  categoryList: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
  },
  categoryItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  categoryLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  categoryIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  categoryName: {
    fontSize: 15,
    fontWeight: '500',
    color: '#1C1917',
    textTransform: 'capitalize',
  },
  categoryRight: {
    alignItems: 'flex-end',
  },
  categoryAmount: {
    fontSize: 15,
    fontWeight: '600',
    color: '#1C1917',
  },
  categoryPercent: {
    fontSize: 12,
    color: '#6B7280',
  },
  transactionList: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 8,
  },
  transactionItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 12,
  },
  transactionLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  transactionIcon: {
    width: 44,
    height: 44,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  transactionIconText: {
    fontSize: 20,
  },
  transactionName: {
    fontSize: 15,
    fontWeight: '500',
    color: '#1C1917',
  },
  transactionCategory: {
    fontSize: 12,
    color: '#6B7280',
    textTransform: 'capitalize',
  },
  transactionAmount: {
    fontSize: 15,
    fontWeight: '600',
  },
  amountNegative: {
    color: '#EF4444',
  },
  amountPositive: {
    color: '#10B981',
  },
  insightsList: {
    backgroundColor: '#FEF3C7',
    borderRadius: 16,
    padding: 16,
  },
  insightItem: {
    marginBottom: 8,
  },
  insightText: {
    fontSize: 14,
    color: '#92400E',
    lineHeight: 20,
  },
  bottomPadding: {
    height: 100,
  },
})
