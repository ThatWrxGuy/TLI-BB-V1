// Busy Bee — AI Suggestions Panel + Push Notification Toggle
// Drop these two components into your app:
//   1. <SuggestionsPanel /> → add as a tab in Domains.jsx (already wired below)
//   2. <PushToggle />       → add to Settings page
//
// NEW Domains.jsx tab: add "🤖 Suggestions" as a third tab after "📡 Radar"

import { useState, useEffect, useCallback } from 'react'
import {
  Box, VStack, HStack, Text, Heading, Card, CardBody, CardHeader,
  Button, Badge, Tag, TagLabel, IconButton, Skeleton, Alert, AlertIcon,
  AlertDescription, Divider, Tooltip, Switch, FormControl, FormLabel,
  Modal, ModalOverlay, ModalContent, ModalHeader, ModalBody, ModalFooter,
  ModalCloseButton, useDisclosure, useToast, SimpleGrid,
} from '@chakra-ui/react'
import {
  FiZap, FiCheck, FiX, FiRefreshCw, FiBell, FiBellOff, FiTarget,
  FiTrendingUp, FiStar,
} from 'react-icons/fi'
import { domainsAPI } from '../services/api'
import { subscribeToPush, unsubscribeFromPush, getPushSubscriptionStatus } from '../services/push'

// ─── Constants ─────────────────────────────────────────────────────────────────

const DOMAIN_META = {
  health:        { color: 'green',  emoji: '🏃', label: 'Health' },
  career:        { color: 'blue',   emoji: '💼', label: 'Career' },
  mindset:       { color: 'purple', emoji: '🧠', label: 'Mindset' },
  habits:        { color: 'orange', emoji: '🔄', label: 'Habits' },
  relationships: { color: 'pink',   emoji: '👥', label: 'Relationships' },
  finance:       { color: 'yellow', emoji: '💰', label: 'Finance' },
}

const DIFFICULTY_META = {
  easy:   { color: 'green',  label: 'Easy',    emoji: '🟢' },
  medium: { color: 'orange', label: 'Medium',  emoji: '🟡' },
  hard:   { color: 'red',    label: 'Stretch', emoji: '🔴' },
}

// ─── Single Suggestion Card ───────────────────────────────────────────────────

function SuggestionCard({ suggestion, onAccept, onDismiss, accepting }) {
  const meta = DOMAIN_META[suggestion.domain_id] || { color: 'gray', emoji: '📌', label: suggestion.domain_id }
  const diff = DIFFICULTY_META[suggestion.difficulty] || DIFFICULTY_META.medium

  return (
    <Card
      borderLeft="3px solid"
      borderLeftColor={`${meta.color}.400`}
      _hover={{ shadow: 'md', transform: 'translateY(-1px)' }}
      transition="all 0.15s"
    >
      <CardBody>
        <VStack align="stretch" spacing={3}>
          {/* Header */}
          <HStack justify="space-between" align="flex-start">
            <HStack spacing={2} flex={1}>
              <Text fontSize="lg">{meta.emoji}</Text>
              <Text fontWeight="600" fontSize="sm" lineHeight="1.3" flex={1}>{suggestion.title}</Text>
            </HStack>
            <Badge colorScheme={diff.color} fontSize="xs" flexShrink={0}>{diff.emoji} {diff.label}</Badge>
          </HStack>

          {/* Description */}
          {suggestion.description && (
            <Text fontSize="xs" color="gray.600" lineHeight="1.5">{suggestion.description}</Text>
          )}

          {/* Why */}
          {suggestion.why && (
            <Box bg="gray.50" borderRadius="md" px={3} py={2} borderLeft="2px solid" borderLeftColor={`${meta.color}.200`}>
              <HStack spacing={1} align="flex-start">
                <Text fontSize="xs" color="gray.400" flexShrink={0}>💡</Text>
                <Text fontSize="xs" color="gray.500" fontStyle="italic">{suggestion.why}</Text>
              </HStack>
            </Box>
          )}

          {/* Tags */}
          <HStack spacing={2} flexWrap="wrap">
            <Tag size="sm" colorScheme={meta.color} variant="subtle">
              <TagLabel>{meta.label}</TagLabel>
            </Tag>
            {suggestion.category && (
              <Badge variant="outline" fontSize="xs">{suggestion.category}</Badge>
            )}
            {suggestion.domain_score !== null && suggestion.domain_score !== undefined && (
              <HStack spacing={1}>
                <FiTrendingUp size={10} color="#A0AEC0" />
                <Text fontSize="xs" color="gray.400">Domain at {suggestion.domain_score}%</Text>
              </HStack>
            )}
          </HStack>

          {/* Actions */}
          <HStack spacing={2} pt={1}>
            <Button
              size="sm"
              colorScheme={meta.color}
              leftIcon={<FiCheck size={12} />}
              flex={1}
              onClick={() => onAccept(suggestion.id)}
              isLoading={accepting === suggestion.id}
              loadingText="Adding…"
            >
              Add Goal
            </Button>
            <Tooltip label="Dismiss this suggestion">
              <IconButton
                icon={<FiX size={14} />}
                size="sm"
                variant="ghost"
                colorScheme="gray"
                onClick={() => onDismiss(suggestion.id)}
                aria-label="Dismiss"
              />
            </Tooltip>
          </HStack>
        </VStack>
      </CardBody>
    </Card>
  )
}

// ─── Suggestions Panel ────────────────────────────────────────────────────────

export function SuggestionsPanel({ allProgress }) {
  const [suggestions, setSuggestions] = useState({})
  const [loading, setLoading]         = useState(true)
  const [generating, setGenerating]   = useState(false)
  const [accepting, setAccepting]     = useState(null)
  const toast = useToast()

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res = await domainsAPI.getSuggestions()
      setSuggestions(res.data?.suggestions || {})
    } catch {
      setSuggestions({})
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const handleGenerate = async () => {
    setGenerating(true)
    try {
      await domainsAPI.generateSuggestions()
      toast({
        title: '🤖 Generating…',
        description: 'AI is analyzing your domains. Suggestions will appear in a few seconds.',
        status: 'info',
        duration: 4000,
      })
      // Poll for results
      setTimeout(async () => {
        await load()
        setGenerating(false)
      }, 5000)
    } catch {
      toast({ title: 'Could not generate suggestions', status: 'error', duration: 2000 })
      setGenerating(false)
    }
  }

  const handleAccept = async (id) => {
    setAccepting(id)
    try {
      const res = await domainsAPI.acceptSuggestion(id, true)
      setSuggestions(prev => {
        const next = { ...prev }
        Object.keys(next).forEach(domain => {
          next[domain] = next[domain].filter(s => s.id !== id)
          if (next[domain].length === 0) delete next[domain]
        })
        return next
      })
      toast({
        title: '🎯 Goal added!',
        description: res.data?.goal?.title,
        status: 'success',
        duration: 2500,
      })
    } catch {
      toast({ title: 'Could not add goal', status: 'error', duration: 2000 })
    } finally {
      setAccepting(null)
    }
  }

  const handleDismiss = async (id) => {
    setSuggestions(prev => {
      const next = { ...prev }
      Object.keys(next).forEach(domain => {
        next[domain] = next[domain].filter(s => s.id !== id)
        if (next[domain].length === 0) delete next[domain]
      })
      return next
    })
    try { await domainsAPI.acceptSuggestion(id, false) } catch {}
  }

  const totalCount = Object.values(suggestions).flat().length
  const domainEntries = Object.entries(suggestions)

  // Find 2 weakest domains from allProgress for context
  const weakDomains = allProgress
    ? Object.entries(allProgress)
        .sort((a, b) => (a[1]?.completion_rate || 0) - (b[1]?.completion_rate || 0))
        .slice(0, 2)
        .map(([id]) => id)
    : []

  return (
    <Card>
      <CardHeader pb={2}>
        <HStack justify="space-between" flexWrap="wrap" gap={2}>
          <VStack align="start" spacing={0}>
            <HStack>
              <Heading size="sm">AI Goal Suggestions</Heading>
              {totalCount > 0 && <Badge colorScheme="brand">{totalCount}</Badge>}
            </HStack>
            <Text fontSize="xs" color="gray.400">Personalized for your weakest domains</Text>
          </VStack>
          <HStack>
            <IconButton icon={<FiRefreshCw />} size="xs" variant="ghost" onClick={load} isLoading={loading} aria-label="Refresh" />
            <Button
              size="xs"
              leftIcon={<FiZap size={11} />}
              colorScheme="brand"
              onClick={handleGenerate}
              isLoading={generating}
              loadingText="Generating…"
            >
              Generate
            </Button>
          </HStack>
        </HStack>
      </CardHeader>

      <CardBody pt={0}>
        {loading ? (
          <VStack spacing={3}>
            {[0, 1, 2].map(i => <Skeleton key={i} height="140px" borderRadius="md" />)}
          </VStack>
        ) : totalCount === 0 ? (
          <VStack py={8} spacing={4} textAlign="center">
            <Text fontSize="3xl">🤖</Text>
            <VStack spacing={1}>
              <Text fontWeight="600" color="gray.700">No suggestions yet</Text>
              <Text fontSize="sm" color="gray.400">
                Click <strong>Generate</strong> and AI will analyze your domains
                and suggest 3 goals each for your 2 weakest areas.
              </Text>
            </VStack>
            {weakDomains.length > 0 && (
              <Alert status="info" borderRadius="md" size="sm">
                <AlertIcon />
                <AlertDescription fontSize="xs">
                  Looks like <strong>{weakDomains.map(d => DOMAIN_META[d]?.label).join(' & ')}</strong> could use some love.
                </AlertDescription>
              </Alert>
            )}
            <Button
              size="sm" colorScheme="brand" leftIcon={<FiZap size={12} />}
              onClick={handleGenerate} isLoading={generating} loadingText="Generating…"
            >
              Generate Suggestions
            </Button>
          </VStack>
        ) : (
          <VStack spacing={5} align="stretch">
            {domainEntries.map(([domainId, sugs]) => {
              const meta = DOMAIN_META[domainId] || { emoji: '📌', label: domainId, color: 'gray' }
              return (
                <Box key={domainId}>
                  <HStack mb={3}>
                    <Text fontSize="xl">{meta.emoji}</Text>
                    <Heading size="xs" color={`${meta.color}.600`}>{meta.label}</Heading>
                    <Badge colorScheme={meta.color} variant="subtle">{sugs.length} ideas</Badge>
                  </HStack>
                  <SimpleGrid columns={{ base: 1, md: sugs.length > 1 ? 2 : 1 }} spacing={3}>
                    {sugs.map(sug => (
                      <SuggestionCard
                        key={sug.id}
                        suggestion={sug}
                        onAccept={handleAccept}
                        onDismiss={handleDismiss}
                        accepting={accepting}
                      />
                    ))}
                  </SimpleGrid>
                  <Divider mt={5} />
                </Box>
              )
            })}
            <Button
              size="sm" variant="ghost" leftIcon={<FiZap size={11} />}
              onClick={handleGenerate} isLoading={generating} alignSelf="center"
            >
              Refresh suggestions
            </Button>
          </VStack>
        )}
      </CardBody>
    </Card>
  )
}

// ─── Push Notification Toggle ──────────────────────────────────────────────────
// Drop into your Settings page:
//   import { PushToggle } from '../components/PushToggle'
//   <PushToggle />

export function PushToggle() {
  const [status, setStatus]     = useState(null)   // { supported, permission, subscribed }
  const [loading, setLoading]   = useState(true)
  const [toggling, setToggling] = useState(false)
  const toast = useToast()

  useEffect(() => {
    getPushSubscriptionStatus().then(s => { setStatus(s); setLoading(false) })
  }, [])

  const handleToggle = async () => {
    setToggling(true)
    try {
      if (status?.subscribed) {
        await unsubscribeFromPush()
        setStatus(prev => ({ ...prev, subscribed: false }))
        toast({ title: '🔕 Notifications off', status: 'info', duration: 2000 })
      } else {
        const sub = await subscribeToPush()
        if (sub) {
          setStatus(prev => ({ ...prev, subscribed: true, permission: 'granted' }))
          toast({ title: '🔔 Notifications on!', description: "You'll get a nudge if you forget to check in.", status: 'success', duration: 3000 })
        } else if (Notification.permission === 'denied') {
          toast({
            title: 'Notifications blocked',
            description: 'Enable them in your browser settings → Site permissions.',
            status: 'warning', duration: 5000,
          })
        }
      }
    } finally { setToggling(false) }
  }

  if (loading) return <Skeleton height="60px" borderRadius="md" />
  if (!status?.supported) return (
    <Alert status="warning" borderRadius="md">
      <AlertIcon />
      <AlertDescription fontSize="sm">Push notifications aren't supported in this browser.</AlertDescription>
    </Alert>
  )

  return (
    <Card>
      <CardBody>
        <HStack justify="space-between" align="center">
          <HStack spacing={3}>
            <Box
              w={10} h={10} borderRadius="full"
              bg={status.subscribed ? 'brand.50' : 'gray.100'}
              display="flex" alignItems="center" justifyContent="center"
            >
              {status.subscribed ? <FiBell color="#F59E0B" size={18} /> : <FiBellOff color="#A0AEC0" size={18} />}
            </Box>
            <VStack align="start" spacing={0}>
              <Text fontWeight="600" fontSize="sm">Check-In Reminders</Text>
              <Text fontSize="xs" color="gray.500">
                {status.subscribed
                  ? 'You\'ll get a nudge if you forget to check in by evening'
                  : status.permission === 'denied'
                    ? 'Blocked in browser — update site permissions to enable'
                    : 'Daily push if you haven\'t checked in. No email spam.'
                }
              </Text>
            </VStack>
          </HStack>
          <Switch
            colorScheme="brand"
            isChecked={status.subscribed}
            onChange={handleToggle}
            isDisabled={toggling || status.permission === 'denied'}
            size="lg"
          />
        </HStack>

        {status.subscribed && (
          <Alert status="success" borderRadius="md" mt={3} py={2}>
            <AlertIcon />
            <AlertDescription fontSize="xs">
              Reminders fire at ~8 PM if no check-ins that day. AI suggestions are also pushed weekly.
            </AlertDescription>
          </Alert>
        )}
      </CardBody>
    </Card>
  )
}
