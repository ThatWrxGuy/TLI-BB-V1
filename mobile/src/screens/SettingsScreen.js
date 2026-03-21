import React, { useState, useEffect } from 'react'
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Switch, Alert } from 'react-native'
import { useAuth } from '../context/AuthContext'
import { profileAPI } from '../services/api'

export default function SettingsScreen() {
  const { user } = useAuth()
  const [settings, setSettings] = useState({
    theme: 'light',
    language: 'en',
    emailNotifications: true,
    pushNotifications: true,
    weeklyDigest: true,
    twoFactorEnabled: false,
  })

  const SettingItem = ({ icon, label, value, type = 'toggle', onPress }) => (
    <TouchableOpacity 
      style={styles.settingItem} 
      onPress={type !== 'toggle' ? onPress : undefined}
      disabled={type === 'toggle'}
    >
      <View style={styles.settingLeft}>
        <Text style={styles.settingIcon}>{icon}</Text>
        <Text style={styles.settingLabel}>{label}</Text>
      </View>
      {type === 'toggle' && (
        <Switch
          value={value}
          onValueChange={onPress}
          trackColor={{ false: '#E5E7EB', true: '#FCD34D' }}
          thumbColor={value ? '#F59E0B' : '#FFFFFF'}
        />
      )}
      {type === 'select' && (
        <Text style={styles.settingValue}>→</Text>
      )}
    </TouchableOpacity>
  )

  const SectionHeader = ({ title }) => (
    <Text style={styles.sectionTitle}>{title}</Text>
  )

  const handleTwoFactor = () => {
    Alert.alert(
      'Two-Factor Authentication',
      settings.twoFactorEnabled 
        ? 'Are you sure you want to disable 2FA?'
        : 'Enable two-factor authentication for extra security?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: settings.twoFactorEnabled ? 'Disable' : 'Enable',
          onPress: () => setSettings({...settings, twoFactorEnabled: !settings.twoFactorEnabled })
        }
      ]
    )
  }

  const handleDeleteAccount = () => {
    Alert.alert(
      'Delete Account',
      'Are you sure you want to delete your account? This action cannot be undone.',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Delete', style: 'destructive', onPress: () => console.log('Delete account') }
      ]
    )
  }

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Settings</Text>
        </View>

        {/* Appearance */}
        <View style={styles.section}>
          <SectionHeader title="Appearance" />
          <View style={styles.card}>
            <SettingItem 
              icon="🌙" 
              label="Theme" 
              value="Light"
              type="select"
              onPress={() => {}}
            />
            <SettingItem 
              icon="🌍" 
              label="Language" 
              value="English"
              type="select"
              onPress={() => {}}
            />
            <SettingItem 
              icon="🕐" 
              label="Timezone" 
              value="UTC",
              type="select"
              onPress={() => {}}
            />
          </View>
        </View>

        {/* Notifications */}
        <View style={styles.section}>
          <SectionHeader title="Notifications" />
          <View style={styles.card}>
            <SettingItem 
              icon="📧" 
              label="Email Notifications" 
              value={settings.emailNotifications}
              onPress={(val) => setSettings({...settings, emailNotifications: val})}
            />
            <SettingItem 
              icon="🔔" 
              label="Push Notifications" 
              value={settings.pushNotifications}
              onPress={(val) => setSettings({...settings, pushNotifications: val})}
            />
            <SettingItem 
              icon="📊" 
              label="Weekly Digest" 
              value={settings.weeklyDigest}
              onPress={(val) => setSettings({...settings, weeklyDigest: val})}
            />
          </View>
        </View>

        {/* Security */}
        <View style={styles.section}>
          <SectionHeader title="Security" />
          <View style={styles.card}>
            <SettingItem 
              icon="🔐" 
              label="Two-Factor Authentication" 
              value={settings.twoFactorEnabled}
              onPress={handleTwoFactor}
            />
            <SettingItem 
              icon="🔑" 
              label="Change Password" 
              type="select"
              onPress={() => {}}
            />
            <SettingItem 
              icon="📱" 
              label="Active Sessions" 
              type="select"
              onPress={() => {}}
            />
          </View>
        </View>

        {/* Privacy */}
        <View style={styles.section}>
          <SectionHeader title="Privacy & Data" />
          <View style={styles.card}>
            <SettingItem 
              icon="📤" 
              label="Export My Data" 
              type="select"
              onPress={() => {}}
            />
            <SettingItem 
              icon="👥" 
              label="Privacy Settings" 
              type="select"
              onPress={() => {}}
            />
          </View>
        </View>

        {/* Danger Zone */}
        <View style={styles.section}>
          <SectionHeader title="Danger Zone" />
          <View style={[styles.card, styles.dangerCard]}>
            <TouchableOpacity style={styles.dangerItem} onPress={handleDeleteAccount}>
              <Text style={styles.dangerIcon}>⚠️</Text>
              <Text style={styles.dangerLabel}>Delete Account</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* App Info */}
        <View style={styles.appInfo}>
          <Text style={styles.appName}>🐝 Busy Bee</Text>
          <Text style={styles.appVersion}>Version 1.0.0</Text>
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
  scrollView: {
    flex: 1,
  },
  header: {
    paddingHorizontal: 20,
    paddingTop: 16,
    paddingBottom: 12,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1C1917',
  },
  section: {
    paddingHorizontal: 20,
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6B7280',
    marginBottom: 8,
    marginLeft: 4,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    overflow: 'hidden',
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  settingLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  settingIcon: {
    fontSize: 20,
    marginRight: 12,
  },
  settingLabel: {
    fontSize: 15,
    fontWeight: '500',
    color: '#1C1917',
  },
  settingValue: {
    fontSize: 16,
    color: '#9CA3AF',
  },
  dangerCard: {
    borderWidth: 1,
    borderColor: '#FEE2E2',
  },
  dangerItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
  },
  dangerIcon: {
    fontSize: 20,
    marginRight: 12,
  },
  dangerLabel: {
    fontSize: 15,
    fontWeight: '500',
    color: '#EF4444',
  },
  appInfo: {
    alignItems: 'center',
    paddingVertical: 20,
  },
  appName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1C1917',
  },
  appVersion: {
    fontSize: 12,
    color: '#9CA3AF',
    marginTop: 4,
  },
  bottomPadding: {
    height: 100,
  },
})
