import { useState, useEffect } from 'react'
import { Box, VStack, HStack, Text, Heading, Button, Card, CardBody, CardHeader, FormControl, FormLabel, Input, Select, Switch, Divider, Alert, AlertIcon, Badge, SimpleGrid } from '@chakra-ui/react'
import { useAuth } from '../context/AuthContext'
import { profileAPI } from '../services/api'

function Settings() {
  const { user } = useAuth()
  const [settings, setSettings] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      const response = await profileAPI.getSettings()
      setSettings(response.data)
    } catch (err) {
      console.error('Failed to load settings:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    // Simulate save
    await new Promise(r => setTimeout(r, 1000))
    setSaving(false)
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  if (loading || !settings) {
    return <Text>Loading...</Text>
  }

  return (
    <VStack spacing={6} align="stretch">
      <Heading size="lg">Settings</Heading>

      {saved && (
        <Alert status="success" borderRadius="lg">
          <AlertIcon />
          Settings saved successfully!
        </Alert>
      )}

      {/* Appearance */}
      <Card>
        <CardHeader>
          <Heading size="sm">Appearance</Heading>
        </CardHeader>
        <CardBody pt={0}>
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
            <FormControl>
              <FormLabel fontSize="sm">Theme</FormLabel>
              <Select defaultValue={settings.theme}>
                <option value="light">Light</option>
                <option value="dark">Dark</option>
                <option value="system">System</option>
              </Select>
            </FormControl>
            <FormControl>
              <FormLabel fontSize="sm">Language</FormLabel>
              <Select defaultValue={settings.language}>
                <option value="en">English</option>
                <option value="es">Spanish</option>
                <option value="fr">French</option>
              </Select>
            </FormControl>
            <FormControl>
              <FormLabel fontSize="sm">Timezone</FormLabel>
              <Select defaultValue={settings.timezone}>
                <option value="UTC">UTC</option>
                <option value="America/New_York">Eastern Time</option>
                <option value="America/Los_Angeles">Pacific Time</option>
              </Select>
            </FormControl>
          </SimpleGrid>
        </CardBody>
      </Card>

      {/* Notifications */}
      <Card>
        <CardHeader>
          <Heading size="sm">Notifications</Heading>
        </CardHeader>
        <CardBody pt={0}>
          <VStack spacing={4} align="stretch">
            <FormControl display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <FormLabel mb={0} fontSize="sm">Email Notifications</FormLabel>
                <Text fontSize="xs" color="gray.500">Receive updates via email</Text>
              </Box>
              <Switch defaultChecked={settings.notifications?.email?.product_updates} />
            </FormControl>
            <Divider />
            <FormControl display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <FormLabel mb={0} fontSize="sm">Push Notifications</FormLabel>
                <Text fontSize="xs" color="gray.500">Receive push alerts</Text>
              </Box>
              <Switch defaultChecked />
            </FormControl>
            <Divider />
            <FormControl display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <FormLabel mb={0} fontSize="sm">Weekly Digest</FormLabel>
                <Text fontSize="xs" color="gray.500">Summary of your week</Text>
              </Box>
              <Switch defaultChecked={settings.notifications?.email?.weekly_digest} />
            </FormControl>
          </VStack>
        </CardBody>
      </Card>

      {/* Security */}
      <Card>
        <CardHeader>
          <Heading size="sm">Security</Heading>
        </CardHeader>
        <CardBody pt={0}>
          <VStack spacing={4} align="stretch">
            <HStack justify="space-between">
              <Box>
                <Text fontWeight="500">Two-Factor Authentication</Text>
                <Text fontSize="sm" color="gray.500">Add extra security to your account</Text>
              </Box>
              <Badge colorScheme={settings.two_factor_enabled ? 'green' : 'gray'}>
                {settings.two_factor_enabled ? 'Enabled' : 'Disabled'}
              </Badge>
            </HStack>
            <Button variant="outline" size="sm" w="fit-content">
              {settings.two_factor_enabled ? 'Manage 2FA' : 'Enable 2FA'}
            </Button>
            <Divider />
            <HStack justify="space-between">
              <Box>
                <Text fontWeight="500">Change Password</Text>
                <Text fontSize="sm" color="gray.500">Update your password</Text>
              </Box>
            </HStack>
            <Button variant="outline" size="sm" w="fit-content">Change Password</Button>
          </VStack>
        </CardBody>
      </Card>

      {/* Danger Zone */}
      <Card borderColor="red.200" border="1px">
        <CardHeader>
          <Heading size="sm" color="red.500">Danger Zone</Heading>
        </CardHeader>
        <CardBody pt={0}>
          <HStack justify="space-between">
            <Box>
              <Text fontWeight="500">Delete Account</Text>
              <Text fontSize="sm" color="gray.500">Permanently delete your account and data</Text>
            </Box>
            <Button colorScheme="red" variant="outline" size="sm">Delete Account</Button>
          </HStack>
        </CardBody>
      </Card>

      <Button colorScheme="brand" size="lg" onClick={handleSave} isLoading={saving}>
        Save Settings
      </Button>
    </VStack>
  )
}

export default Settings
