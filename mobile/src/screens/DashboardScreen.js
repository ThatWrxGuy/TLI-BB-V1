import React, { useState, useEffect } from 'react'
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, RefreshControl, FlatList } from 'react-native'
import { useAuth } from '../context/AuthContext'
import { dashboardAPI } from '../services/api'

export default function DashboardScreen() {
  const { user } = useAuth()
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [data, setData] = useState(null)

  useEffect(() => {
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    try {
      const response = await dashboardAPI.getDashboard()
      setData(response.data)
    } catch (err) {
      console.error('Failed to load dashboard:', err)
    } finally {
      setLoading(false)
    }
  }

  const onRefresh = async () => {
    setRefreshing(true)
    await loadDashboard()
    setRefreshing(false)
  }

  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Good morning'
    if (hour < 18) return 'Good afternoon'
    return 'Good evening'
  }

  const StatCard = ({ icon, label, value, trend }) => (
    <View style={styles.statCard}>
      <Text style={styles.statIcon}>{icon}</Text>
      <Text style={styles.statValue}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  )

  const GoalCard = ({ goal }) => (
    <View style={styles.goalCard}>
      <View style={styles.goalHeader}>
        <Text style={styles.goalTitle}>{goal.title}</Text>
        <View style={[styles.badge, goal.status === 'active' && styles.badgeActive]}>
          <Text style={styles.badgeText}>{goal.status}</Text>
        </View>
      </View>
      <View style={styles.progressBar}>
        <View style={[styles.progressFill, { width: `${goal.progress}%` }]} />
      </View>
      <Text style={styles.goalProgress}>{goal.progress}% complete</Text>
    </View>
  )

  const TaskItem = ({ task }) => (
    <TouchableOpacity style={styles.taskItem}>
      <View style={[styles.checkbox, task.is_completed && styles.checkboxChecked]}>
        {task.is_completed && <Text style={styles.checkmark}>✓</Text>}
      </View>
      <View style={styles.taskContent}>
        <Text style={[styles.taskTitle, task.is_completed && styles.taskTitleDone]}>
          {task.title}
        </Text>
        {task.due_date && <Text style={styles.taskDue}>{task.due_date}</Text>}
      </View>
    </TouchableOpacity>
  )

  const QuickAction = ({ icon, label }) => (
    <TouchableOpacity style={styles.quickAction}>
      <Text style={styles.quickActionIcon}>{icon}</Text>
      <Text style={styles.quickActionLabel}>{label}</Text>
    </TouchableOpacity>
  )

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    )
  }

  const overview = data?.overview || {}
  const goals = data?.goals || []
  const tasks = data?.tasks || []

  return (
    <View style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>{getGreeting()}</Text>
            <Text style={styles.userName}>{user?.full_name || 'User'}</Text>
          </View>
          <TouchableOpacity style={styles.notificationBtn}>
            <Text>🔔</Text>
          </TouchableOpacity>
        </View>

        {/* Stats */}
        <View style={styles.statsContainer}>
          <StatCard icon="🎯" label="Goals" value={overview.active_goals || 0} />
          <StatCard icon="✅" label="Done" value={overview.completed_goals || 0} />
          <StatCard icon="📋" label="Tasks" value={tasks.filter(t => !t.is_completed).length} />
          <StatCard icon="🔥" label="Streak" value={`${overview.streak_days || 0}d`} />
        </View>

        {/* Goals Section */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Goals</Text>
            <TouchableOpacity>
              <Text style={styles.seeAll}>See all</Text>
            </TouchableOpacity>
          </View>
          {goals.length > 0 ? (
            goals.slice(0, 3).map(goal => <GoalCard key={goal.id} goal={goal} />)
          ) : (
            <View style={styles.emptyState}>
              <Text style={styles.emptyText}>No goals yet</Text>
            </View>
          )}
        </View>

        {/* Quick Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.quickActionsGrid}>
            <QuickAction icon="➕" label="New Goal" />
            <QuickAction icon="📝" label="Add Task" />
            <QuickAction icon="💬" label="AI Chat" />
            <QuickAction icon="📊" label="Reports" />
          </View>
        </View>

        {/* Tasks Section */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Tasks</Text>
            <TouchableOpacity>
              <Text style={styles.seeAll}>See all</Text>
            </TouchableOpacity>
          </View>
          {tasks.length > 0 ? (
            tasks.slice(0, 5).map(task => <TaskItem key={task.id} task={task} />)
          ) : (
            <View style={styles.emptyState}>
              <Text style={styles.emptyText}>No tasks yet</Text>
            </View>
          )}
        </View>

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
    paddingBottom: 20,
  },
  greeting: {
    fontSize: 14,
    color: '#6B7280',
  },
  userName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1C1917',
  },
  notificationBtn: {
    width: 44,
    height: 44,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  statsContainer: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    marginBottom: 24,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    marginHorizontal: 4,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  statIcon: {
    fontSize: 24,
    marginBottom: 8,
  },
  statValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1C1917',
  },
  statLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 4,
  },
  section: {
    paddingHorizontal: 20,
    marginBottom: 24,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1C1917',
  },
  seeAll: {
    fontSize: 14,
    color: '#F59E0B',
    fontWeight: '500',
  },
  goalCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  goalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  goalTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1C1917',
  },
  badge: {
    backgroundColor: '#E5E7EB',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  badgeActive: {
    backgroundColor: '#D1FAE5',
  },
  badgeText: {
    fontSize: 12,
    color: '#6B7280',
    textTransform: 'capitalize',
  },
  progressBar: {
    height: 8,
    backgroundColor: '#E5E7EB',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#F59E0B',
    borderRadius: 4,
  },
  goalProgress: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 8,
  },
  quickActionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  quickAction: {
    width: '48%',
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    alignItems: 'center',
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  quickActionIcon: {
    fontSize: 28,
    marginBottom: 8,
  },
  quickActionLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: '#374151',
  },
  taskItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 14,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.03,
    shadowRadius: 2,
    elevation: 1,
  },
  checkbox: {
    width: 24,
    height: 24,
    borderRadius: 6,
    borderWidth: 2,
    borderColor: '#D1D5DB',
    marginRight: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkboxChecked: {
    backgroundColor: '#10B981',
    borderColor: '#10B981',
  },
  checkmark: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: 'bold',
  },
  taskContent: {
    flex: 1,
  },
  taskTitle: {
    fontSize: 15,
    fontWeight: '500',
    color: '#1C1917',
  },
  taskTitleDone: {
    textDecorationLine: 'line-through',
    color: '#9CA3AF',
  },
  taskDue: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 4,
  },
  emptyState: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
  },
  emptyText: {
    color: '#9CA3AF',
    fontSize: 14,
  },
  bottomPadding: {
    height: 100,
  },
})
