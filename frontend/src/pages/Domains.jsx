// Busy Bee — Life Domains Page (v3)
// Drop-in replacement for frontend/src/pages/Domains.jsx
// New in v3: weekly radar chart (pure SVG), snapshot history, trend arrows per domain

import { useState, useEffect, useRef, useCallback } from 'react'
import {
  Box, VStack, HStack, Text, Heading, Card, CardBody, CardHeader,
  SimpleGrid, Badge, Button, Progress, IconButton, Input, Textarea,
  Select, Modal, ModalOverlay, ModalContent, ModalHeader, ModalBody,
  ModalFooter, ModalCloseButton, useDisclosure, useToast, Tooltip, Flex,
  CircularProgress, CircularProgressLabel, Skeleton, SkeletonText,
  Tag, TagLabel, Divider, Alert, AlertIcon, AlertDescription,
  Tabs, TabList, Tab, TabPanels, TabPanel,
} from '@chakra-ui/react'
import {
  FiPlus, FiArrowLeft, FiZap, FiTarget, FiCheck, FiCalendar,
  FiTrendingUp, FiTrendingDown, FiMinus, FiAward, FiRefreshCw,
  FiCheckCircle, FiCamera,
} from 'react-icons/fi'
import { domainsAPI } from '../services/api'

// ─── Constants ─────────────────────────────────────────────────────────────────

const DOMAIN_META = {
  health:        { color: 'green',  hex: '#38A169', label: 'Health',        emoji: '🏃' },
  career:        { color: 'blue',   hex: '#3182CE', label: 'Career',        emoji: '💼' },
  mindset:       { color: 'purple', hex: '#805AD5', label: 'Mindset',       emoji: '🧠' },
  habits:        { color: 'orange', hex: '#DD6B20', label: 'Habits',        emoji: '🔄' },
  relationships: { color: 'pink',   hex: '#D53F8C', label: 'Relationships', emoji: '👥' },
  finance:       { color: 'yellow', hex: '#D69E2E', label: 'Finance',       emoji: '💰' },
}

const DOMAIN_ORDER = ['health', 'career', 'mindset', 'habits', 'relationships', 'finance']
const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

function getTodayKey() {
  return new Date().toISOString().slice(0, 10)
}

// ─── Radar Chart (pure SVG) ────────────────────────────────────────────────────
//
// axes  = ['health','career','mindset','habits','relationships','finance']
// data  = array of { label, values: { [axisKey]: 0-100 } }  (one entry per week or "live")
// size  = px (square)

function RadarChart({ data, size = 280 }) {
  const cx = size / 2
  const cy = size / 2
  const R  = size * 0.36    // outer radius of the chart area
  const n  = DOMAIN_ORDER.length
  const levels = [20, 40, 60, 80, 100]

  // Angle for each axis (clockwise from top)
  const angle = i => (Math.PI * 2 * i) / n - Math.PI / 2

  // Convert value (0-100) + axis index to SVG x,y
  const point = (val, i) => {
    const r = (val / 100) * R
    return [cx + r * Math.cos(angle(i)), cy + r * Math.sin(angle(i))]
  }

  // Grid rings
  const rings = levels.map(lvl => {
    const pts = DOMAIN_ORDER.map((_, i) => point(lvl, i).join(','))
    return <polygon key={lvl} points={pts.join(' ')} fill="none" stroke="#E2E8F0" strokeWidth={1} />
  })

  // Axis lines
  const axes = DOMAIN_ORDER.map((id, i) => {
    const [x, y] = point(100, i)
    return <line key={id} x1={cx} y1={cy} x2={x} y2={y} stroke="#CBD5E0" strokeWidth={1} />
  })

  // Axis labels
  const labels = DOMAIN_ORDER.map((id, i) => {
    const [x, y] = point(118, i)
    const meta = DOMAIN_META[id]
    return (
      <text
        key={id}
        x={x} y={y}
        textAnchor="middle"
        dominantBaseline="middle"
        fontSize={10}
        fontWeight="600"
        fill="#4A5568"
      >
        {meta.emoji} {meta.label}
      </text>
    )
  })

  // Data polygons — render oldest first (most transparent) → newest last (solid)
  const polygons = data.map((series, si) => {
    if (!series.values) return null
    const pts = DOMAIN_ORDER.map((id, i) => point(series.values[id] || 0, i).join(','))
    const isLive = series.isLive
    const opacity = isLive ? 0.9 : 0.15 + (si / (data.length)) * 0.55
    const strokeOpacity = isLive ? 1 : 0.3 + (si / data.length) * 0.5

    return (
      <g key={si}>
        <polygon
          points={pts.join(' ')}
          fill={isLive ? 'rgba(245,158,11,0.15)' : 'rgba(99,179,237,0.1)'}
          stroke={isLive ? '#F59E0B' : '#63B3ED'}
          strokeWidth={isLive ? 2.5 : 1.5}
          strokeOpacity={strokeOpacity}
          fillOpacity={opacity * 0.4}
        />
        {/* Dots on live series */}
        {isLive && DOMAIN_ORDER.map((id, i) => {
          const [px, py] = point(series.values[id] || 0, i)
          const meta = DOMAIN_META[id]
          return (
            <Tooltip key={id} label={`${meta.label}: ${series.values[id] || 0}%`}>
              <circle cx={px} cy={py} r={4} fill={meta.hex} stroke="white" strokeWidth={1.5} style={{ cursor: 'pointer' }} />
            </Tooltip>
          )
        })}
      </g>
    )
  })

  // Center score
  const liveData = data.find(d => d.isLive)
  const avgScore = liveData
    ? Math.round(DOMAIN_ORDER.reduce((s, id) => s + (liveData.values[id] || 0), 0) / DOMAIN_ORDER.length)
    : null

  return (
    <svg width={size} height={size} style={{ display: 'block', margin: '0 auto', overflow: 'visible' }}>
      {rings}
      {axes}
      {polygons}
      {labels}
      {/* Level labels on the right axis */}
      {levels.map(lvl => {
        const [lx, ly] = point(lvl, 0)
        return (
          <text key={lvl} x={lx + 4} y={ly} fontSize={8} fill="#A0AEC0">{lvl}</text>
        )
      })}
      {/* Center score */}
      {avgScore !== null && (
        <>
          <circle cx={cx} cy={cy} r={22} fill="white" stroke="#E2E8F0" strokeWidth={1} />
          <text x={cx} y={cy - 4} textAnchor="middle" fontSize={14} fontWeight="700" fill="#2D3748">{avgScore}</text>
          <text x={cx} y={cy + 10} textAnchor="middle" fontSize={8} fill="#718096">avg</text>
        </>
      )}
    </svg>
  )
}

// ─── Radar Panel ───────────────────────────────────────────────────────────────

function RadarPanel({ allProgress }) {
  const [radarData, setRadarData]     = useState(null)
  const [loading, setLoading]         = useState(true)
  const [snapshotting, setSnapshotting] = useState(false)
  const [weeksToShow, setWeeksToShow] = useState(4)
  const toast = useToast()

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res = await domainsAPI.getRadarData(weeksToShow)
      setRadarData(res.data)
    } catch {
      // No snapshots yet — fall back to live data only
      setRadarData(null)
    } finally {
      setLoading(false)
    }
  }, [weeksToShow])

  useEffect(() => { load() }, [load])

  const handleSnapshot = async () => {
    setSnapshotting(true)
    try {
      await domainsAPI.triggerSnapshot()
      toast({ title: '📸 Snapshot saved!', description: 'This week\'s scores have been recorded.', status: 'success', duration: 3000 })
      await load()
    } catch {
      toast({ title: 'Snapshot failed', status: 'error', duration: 2000 })
    } finally {
      setSnapshotting(false)
    }
  }

  // Build chart data array: historical weeks + live "this week"
  const buildChartData = () => {
    const live = allProgress
      ? { label: 'This Week (live)', isLive: true, values: Object.fromEntries(DOMAIN_ORDER.map(id => [id, allProgress[id]?.completion_rate || 0])) }
      : null

    if (!radarData?.weeks || !radarData?.series) {
      return live ? [live] : []
    }

    const historicalSeries = radarData.weeks.slice(0, -1).map((week, wi) => ({
      label: week,
      isLive: false,
      values: Object.fromEntries(DOMAIN_ORDER.map(id => [id, radarData.series[id]?.[wi] || 0])),
    })).filter(s => DOMAIN_ORDER.some(id => s.values[id] > 0))

    return live ? [...historicalSeries, live] : historicalSeries
  }

  const chartData = buildChartData()

  // Compute week-over-week trend per domain
  const trends = {}
  if (radarData?.series && radarData?.live) {
    DOMAIN_ORDER.forEach(id => {
      const series = radarData.series[id] || []
      const prev = [...series].reverse().find(v => v != null)
      const curr = radarData.live[id] || 0
      trends[id] = prev != null ? Math.round(curr - prev) : null
    })
  }

  return (
    <Card>
      <CardHeader pb={2}>
        <HStack justify="space-between" flexWrap="wrap" gap={2}>
          <VStack align="start" spacing={0}>
            <Heading size="sm">Life Balance Radar</Heading>
            <Text fontSize="xs" color="gray.400">How your domains compare week over week</Text>
          </VStack>
          <HStack>
            <Select
              size="xs"
              value={weeksToShow}
              onChange={e => setWeeksToShow(Number(e.target.value))}
              w="auto"
            >
              <option value={4}>4 weeks</option>
              <option value={8}>8 weeks</option>
              <option value={12}>12 weeks</option>
            </Select>
            <Tooltip label="Save this week's snapshot">
              <Button
                size="xs"
                leftIcon={<FiCamera />}
                onClick={handleSnapshot}
                isLoading={snapshotting}
                colorScheme="brand"
                variant="outline"
              >
                Snapshot
              </Button>
            </Tooltip>
            <IconButton icon={<FiRefreshCw />} size="xs" variant="ghost" onClick={load} isLoading={loading} aria-label="Refresh" />
          </HStack>
        </HStack>
      </CardHeader>
      <CardBody pt={0}>
        {loading ? (
          <Skeleton height="300px" borderRadius="md" />
        ) : chartData.length === 0 ? (
          <VStack py={8} spacing={3}>
            <Text fontSize="3xl">📊</Text>
            <Text color="gray.500" textAlign="center">No snapshot history yet.</Text>
            <Text fontSize="sm" color="gray.400" textAlign="center">
              Click <strong>Snapshot</strong> to record this week's scores.
              It'll happen automatically every Sunday.
            </Text>
            <Button size="sm" leftIcon={<FiCamera />} colorScheme="brand" onClick={handleSnapshot} isLoading={snapshotting}>
              Take First Snapshot
            </Button>
          </VStack>
        ) : (
          <VStack spacing={4}>
            <RadarChart data={chartData} size={300} />

            {/* Legend */}
            <HStack spacing={4} flexWrap="wrap" justify="center">
              {chartData.map((s, i) => (
                <HStack key={i} spacing={1}>
                  <Box
                    w={3} h={3} borderRadius="sm"
                    bg={s.isLive ? '#F59E0B' : '#63B3ED'}
                    opacity={s.isLive ? 1 : 0.4 + (i / chartData.length) * 0.6}
                  />
                  <Text fontSize="xs" color="gray.500">
                    {s.isLive ? 'This week (live)' : s.label}
                  </Text>
                </HStack>
              ))}
            </HStack>

            {/* Trend row */}
            {Object.keys(trends).length > 0 && (
              <>
                <Divider />
                <SimpleGrid columns={3} spacing={2} w="full">
                  {DOMAIN_ORDER.map(id => {
                    const meta = DOMAIN_META[id]
                    const t = trends[id]
                    const live = allProgress?.[id]?.completion_rate || 0
                    return (
                      <HStack key={id} spacing={2} p={2} bg="gray.50" borderRadius="md">
                        <Text fontSize="lg">{meta.emoji}</Text>
                        <VStack align="start" spacing={0} flex={1} minW={0}>
                          <Text fontSize="xs" fontWeight="600" noOfLines={1}>{meta.label}</Text>
                          <Text fontSize="xs" color="gray.500">{live}%</Text>
                        </VStack>
                        {t !== null && (
                          <HStack spacing={0.5} fontSize="xs" fontWeight="bold"
                            color={t > 0 ? 'green.500' : t < 0 ? 'red.400' : 'gray.400'}
                          >
                            {t > 0 ? <FiTrendingUp size={12} /> : t < 0 ? <FiTrendingDown size={12} /> : <FiMinus size={12} />}
                            <Text>{t > 0 ? '+' : ''}{t}%</Text>
                          </HStack>
                        )}
                      </HStack>
                    )
                  })}
                </SimpleGrid>
              </>
            )}
          </VStack>
        )}
      </CardBody>
    </Card>
  )
}

// ─── Animated Ring ─────────────────────────────────────────────────────────────

function DomainRing({ value, color, size = 80 }) {
  const [displayed, setDisplayed] = useState(0)
  useEffect(() => {
    let frame
    const target = value || 0
    const step = () => setDisplayed(prev => {
      if (prev >= target) return target
      frame = requestAnimationFrame(step)
      return prev + Math.ceil((target - prev) / 6)
    })
    frame = requestAnimationFrame(step)
    return () => cancelAnimationFrame(frame)
  }, [value])
  return (
    <CircularProgress value={displayed} color={`${color}.400`} trackColor="gray.100" size={`${size}px`} thickness="10px">
      <CircularProgressLabel fontSize="sm" fontWeight="bold" color={`${color}.600`}>{displayed}%</CircularProgressLabel>
    </CircularProgress>
  )
}

// ─── Domain Card ───────────────────────────────────────────────────────────────

function DomainCard({ domain, progress, checkedInToday, trend, onSelect, onQuickCheckin }) {
  const meta = DOMAIN_META[domain.id] || { color: 'gray', emoji: '📌' }
  const isChecked = checkedInToday[domain.id]

  return (
    <Card
      cursor="pointer"
      onClick={() => onSelect(domain)}
      _hover={{ transform: 'translateY(-3px)', shadow: 'lg' }}
      transition="all 0.2s"
      borderTop="4px solid"
      borderTopColor={`${meta.color}.400`}
      position="relative"
    >
      {isChecked && (
        <Box position="absolute" top={-2} right={-2} bg="green.400" color="white"
          borderRadius="full" w={6} h={6} display="flex" alignItems="center"
          justifyContent="center" fontSize="xs" shadow="sm" zIndex={1}>✓</Box>
      )}
      <CardBody>
        <VStack align="stretch" spacing={3}>
          <HStack justify="space-between">
            <Text fontSize="2xl">{domain.icon || meta.emoji}</Text>
            <VStack align="flex-end" spacing={0}>
              <DomainRing value={progress?.completion_rate || 0} color={meta.color} size={60} />
              {trend !== null && trend !== undefined && (
                <HStack spacing={0.5} fontSize="xs" fontWeight="bold"
                  color={trend > 0 ? 'green.500' : trend < 0 ? 'red.400' : 'gray.400'}
                  mt={0.5}
                >
                  {trend > 0 ? <FiTrendingUp size={10} /> : trend < 0 ? <FiTrendingDown size={10} /> : <FiMinus size={10} />}
                  <Text>{trend > 0 ? '+' : ''}{trend}%</Text>
                </HStack>
              )}
            </VStack>
          </HStack>

          <VStack align="stretch" spacing={0}>
            <Heading size="sm">{domain.name}</Heading>
            <Text fontSize="xs" color="gray.500" noOfLines={2}>{domain.description}</Text>
          </VStack>

          <HStack spacing={2} flexWrap="wrap">
            <Tag size="sm" colorScheme={meta.color} variant="subtle">
              <TagLabel>{progress?.active_goals || 0} goals</TagLabel>
            </Tag>
            <Tag size="sm" colorScheme="orange" variant="subtle">
              <TagLabel>🔥 {progress?.current_streak || 0}d</TagLabel>
            </Tag>
            <Tag size="sm" colorScheme="gray" variant="subtle">
              <TagLabel>{progress?.weekly_checkins || 0}/7</TagLabel>
            </Tag>
          </HStack>

          <Button
            size="sm"
            colorScheme={isChecked ? 'green' : meta.color}
            variant={isChecked ? 'solid' : 'outline'}
            leftIcon={isChecked ? <FiCheckCircle /> : <FiCheck />}
            onClick={e => { e.stopPropagation(); onQuickCheckin(domain.id, isChecked) }}
            isDisabled={isChecked}
          >
            {isChecked ? 'Checked In ✓' : 'Check In Today'}
          </Button>
        </VStack>
      </CardBody>
    </Card>
  )
}

// ─── Weekly Heatmap ────────────────────────────────────────────────────────────

function WeeklyHeatmap({ domainsData }) {
  const today = new Date()
  const week = Array.from({ length: 7 }, (_, i) => {
    const d = new Date(today); d.setDate(today.getDate() - (6 - i))
    return { label: DAYS[d.getDay()], date: d.toISOString().slice(0, 10), isToday: i === 6 }
  })
  const checkinMap = {}
  domainsData.forEach(({ checkins }) => {
    if (!checkins) return
    checkins.forEach(c => { if (c.status === 'completed') checkinMap[c.date] = (checkinMap[c.date] || 0) + 1 })
  })
  const total = domainsData.length || 6
  const getColor = count => {
    if (!count) return 'gray.100'
    const pct = count / total
    if (pct >= 0.8) return 'green.400'
    if (pct >= 0.5) return 'green.200'
    if (pct >= 0.25) return 'yellow.200'
    return 'red.100'
  }
  return (
    <Card>
      <CardHeader pb={2}>
        <HStack justify="space-between">
          <Heading size="sm">This Week</Heading>
          <Text fontSize="xs" color="gray.400">Cross-domain activity</Text>
        </HStack>
      </CardHeader>
      <CardBody pt={0}>
        <HStack spacing={2} justify="space-between">
          {week.map(day => (
            <VStack key={day.date} spacing={1} flex={1}>
              <Text fontSize="xs" fontWeight={day.isToday ? '700' : '400'} color={day.isToday ? 'brand.600' : 'gray.500'}>
                {day.label}
              </Text>
              <Tooltip label={`${checkinMap[day.date] || 0}/${total} domains`}>
                <Box w="full" h={10} borderRadius="md" bg={getColor(checkinMap[day.date])}
                  display="flex" alignItems="center" justifyContent="center"
                  border={day.isToday ? '2px solid' : '1px solid'}
                  borderColor={day.isToday ? 'brand.400' : 'transparent'}
                >
                  <Text fontSize="xs" fontWeight="600" color="gray.600">
                    {checkinMap[day.date] || ''}
                  </Text>
                </Box>
              </Tooltip>
            </VStack>
          ))}
        </HStack>
        <HStack mt={3} spacing={3} justify="flex-end">
          {[{color:'gray.100',label:'None'},{color:'red.100',label:'Low'},{color:'yellow.200',label:'Mid'},{color:'green.200',label:'Good'},{color:'green.400',label:'Full'}]
            .map(({color,label}) => (
              <HStack key={label} spacing={1}>
                <Box w={3} h={3} borderRadius="sm" bg={color} border="1px solid" borderColor="gray.200" />
                <Text fontSize="xs" color="gray.400">{label}</Text>
              </HStack>
          ))}
        </HStack>
      </CardBody>
    </Card>
  )
}

// ─── Motivational Insight ──────────────────────────────────────────────────────

function InsightBar({ allProgress }) {
  if (!allProgress || !Object.keys(allProgress).length) return null
  const entries = Object.entries(allProgress)
  const best    = entries.reduce((a, b) => (b[1]?.completion_rate > a[1]?.completion_rate ? b : a))
  const weakest = entries.reduce((a, b) => (b[1]?.completion_rate < a[1]?.completion_rate ? b : a))
  const topStreak = entries.reduce((a, b) => (b[1]?.current_streak > a[1]?.current_streak ? b : a))
  const meta = id => DOMAIN_META[id] || { emoji: '📌', label: id }
  const insights = [
    `${meta(best[0]).emoji} ${meta(best[0]).label} is your strongest domain at ${best[1]?.completion_rate}% — keep that momentum!`,
    `🔥 ${meta(topStreak[0]).emoji} ${meta(topStreak[0]).label} has your longest streak: ${topStreak[1]?.current_streak} days. Don't break the chain.`,
    `⚡ ${meta(weakest[0]).emoji} ${meta(weakest[0]).label} needs some love (${weakest[1]?.completion_rate}%). Even one small action today moves the needle.`,
  ]
  const insight = insights[new Date().getDate() % insights.length]
  return (
    <Alert status="info" borderRadius="lg" bg="brand.50" border="1px solid" borderColor="brand.200">
      <AlertIcon color="brand.500" />
      <AlertDescription fontSize="sm" color="gray.700">{insight}</AlertDescription>
    </Alert>
  )
}

// ─── New Goal Modal ────────────────────────────────────────────────────────────

function NewGoalModal({ isOpen, onClose, domain, onGoalCreated }) {
  const [title, setTitle]           = useState('')
  const [description, setDescription] = useState('')
  const [category, setCategory]     = useState('')
  const [targetDate, setTargetDate] = useState('')
  const [saving, setSaving]         = useState(false)
  const toast = useToast()
  const meta = DOMAIN_META[domain?.id] || { color: 'brand' }

  const handleSubmit = async () => {
    if (!title.trim()) { toast({ title: 'Add a title', status: 'warning', duration: 2000 }); return }
    setSaving(true)
    try {
      const res = await domainsAPI.createGoal(domain.id, title, description, category, targetDate)
      onGoalCreated?.(res.data)
      toast({ title: '🎯 Goal created!', status: 'success', duration: 2000 })
      setTitle(''); setDescription(''); setCategory(''); setTargetDate('')
      onClose()
    } catch (err) {
      toast({ title: 'Could not create goal', description: err.message, status: 'error', duration: 3000 })
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="md">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>New {domain?.name} Goal</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <VStack spacing={4}>
            <Input placeholder="Goal title" value={title} onChange={e => setTitle(e.target.value)} focusBorderColor={`${meta.color}.400`} autoFocus />
            <Textarea placeholder="Description (optional)" value={description} onChange={e => setDescription(e.target.value)} focusBorderColor={`${meta.color}.400`} rows={2} />
            <HStack w="full">
              <Select placeholder="Category" value={category} onChange={e => setCategory(e.target.value)} focusBorderColor={`${meta.color}.400`}>
                {(domain?.categories || []).map(c => <option key={c} value={c}>{c}</option>)}
              </Select>
              <Input type="date" value={targetDate} onChange={e => setTargetDate(e.target.value)} focusBorderColor={`${meta.color}.400`} />
            </HStack>
          </VStack>
        </ModalBody>
        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose}>Cancel</Button>
          <Button colorScheme={meta.color || 'brand'} onClick={handleSubmit} isLoading={saving} leftIcon={<FiTarget />}>Create Goal</Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}

// ─── Domain Detail Panel ───────────────────────────────────────────────────────

function DomainDetail({ domain, onBack }) {
  const meta = DOMAIN_META[domain.id] || { color: 'gray', emoji: '📌' }
  const [progress, setProgress] = useState(null)
  const [goals, setGoals]       = useState([])
  const [checkins, setCheckins] = useState([])
  const [loading, setLoading]   = useState(true)
  const { isOpen, onOpen, onClose } = useDisclosure()
  const toast = useToast()

  useEffect(() => {
    Promise.all([
      domainsAPI.getDomainProgress(domain.id).catch(() => ({ data: {} })),
      domainsAPI.getDomainGoals(domain.id).catch(() => ({ data: [] })),
      domainsAPI.getDomainCheckins(domain.id, 28).catch(() => ({ data: [] })),
    ]).then(([p, g, c]) => {
      setProgress(p.data)
      setGoals(g.data || [])
      setCheckins(c.data || [])
    }).finally(() => setLoading(false))
  }, [domain.id])

  const handleGoalCreated = (newGoal) => {
    setGoals(prev => [newGoal, ...prev])
  }

  if (loading) return (
    <VStack spacing={4} align="stretch">
      <Button variant="ghost" leftIcon={<FiArrowLeft />} onClick={onBack} alignSelf="flex-start">Back</Button>
      <SkeletonText noOfLines={8} spacing={4} />
    </VStack>
  )

  const checkinDates = new Set(checkins.filter(c => c.status === 'completed').map(c => c.date))
  const today = getTodayKey()
  const last28 = Array.from({ length: 28 }, (_, i) => {
    const d = new Date(); d.setDate(d.getDate() - (27 - i))
    return d.toISOString().slice(0, 10)
  })

  return (
    <VStack spacing={5} align="stretch">
      <HStack justify="space-between" flexWrap="wrap" gap={2}>
        <Button variant="ghost" leftIcon={<FiArrowLeft />} onClick={onBack}>All Domains</Button>
        <Button leftIcon={<FiPlus />} colorScheme={meta.color} onClick={onOpen} size="sm">New Goal</Button>
      </HStack>

      {/* Domain header */}
      <Card borderTop="4px solid" borderTopColor={`${meta.color}.400`}>
        <CardBody>
          <HStack spacing={4} align="flex-start">
            <Text fontSize="3xl">{domain.icon || meta.emoji}</Text>
            <VStack align="start" spacing={1} flex={1}>
              <HStack>
                <Heading size="md">{domain.name}</Heading>
                <Badge colorScheme={meta.color}>{progress?.completion_rate || 0}%</Badge>
              </HStack>
              <Text fontSize="sm" color="gray.500">{domain.description}</Text>
              <HStack spacing={3} flexWrap="wrap">
                <Tag size="sm" colorScheme={meta.color} variant="subtle"><TagLabel>{progress?.active_goals || 0} active goals</TagLabel></Tag>
                <Tag size="sm" colorScheme="orange"  variant="subtle"><TagLabel>🔥 {progress?.current_streak || 0} day streak</TagLabel></Tag>
                <Tag size="sm" colorScheme="green"   variant="subtle"><TagLabel>{progress?.completed_goals || 0} completed</TagLabel></Tag>
              </HStack>
            </VStack>
            <DomainRing value={progress?.completion_rate || 0} color={meta.color} size={80} />
          </HStack>
        </CardBody>
      </Card>

      {/* Check-in calendar (28 days) */}
      <Card>
        <CardHeader pb={2}><Heading size="sm">28-Day Check-in History</Heading></CardHeader>
        <CardBody pt={0}>
          <SimpleGrid columns={7} spacing={1}>
            {DAYS.map(d => <Text key={d} fontSize="xs" color="gray.400" textAlign="center">{d}</Text>)}
            {last28.map(date => {
              const status = checkinDates.has(date) ? 'completed' : 'none'
              const isToday = date === today
              return (
                <Tooltip key={date} label={date}>
                  <Box
                    h={6} borderRadius="sm"
                    bg={status === 'completed' ? `${meta.color}.400` : 'gray.100'}
                    border={isToday ? '2px solid' : '1px solid'}
                    borderColor={isToday ? `${meta.color}.500` : 'transparent'}
                    cursor="default"
                  />
                </Tooltip>
              )
            })}
          </SimpleGrid>
        </CardBody>
      </Card>

      {/* Goals */}
      <Card>
        <CardHeader pb={0}>
          <HStack justify="space-between">
            <Heading size="sm">Goals</Heading>
            <Badge colorScheme={meta.color}>{goals.length}</Badge>
          </HStack>
        </CardHeader>
        <CardBody>
          {goals.length === 0 ? (
            <VStack py={4} spacing={2}>
              <Text color="gray.400">No goals yet.</Text>
              <Button size="sm" leftIcon={<FiPlus />} colorScheme={meta.color} onClick={onOpen}>Add first goal</Button>
            </VStack>
          ) : (
            <VStack spacing={3} align="stretch">
              {goals.map(g => (
                <Box key={g.id} p={3} bg="gray.50" borderRadius="md">
                  <HStack justify="space-between" mb={1}>
                    <Text fontWeight="500" fontSize="sm">{g.title}</Text>
                    <Badge colorScheme={g.status === 'active' ? 'green' : g.status === 'completed' ? 'blue' : 'gray'} fontSize="xs">{g.status}</Badge>
                  </HStack>
                  <Progress value={g.progress} colorScheme={meta.color} size="sm" borderRadius="full" />
                  <HStack justify="space-between" mt={1}>
                    <Text fontSize="xs" color="gray.500">{g.progress}%</Text>
                    {g.category && <Badge variant="outline" fontSize="xs">{g.category}</Badge>}
                  </HStack>
                </Box>
              ))}
            </VStack>
          )}
        </CardBody>
      </Card>

      <NewGoalModal isOpen={isOpen} onClose={onClose} domain={domain} onGoalCreated={handleGoalCreated} />
    </VStack>
  )
}

// ─── Main Domains Page ─────────────────────────────────────────────────────────

function Domains() {
  const [domains, setDomains]       = useState([])
  const [allProgress, setAllProgress] = useState({})
  const [domainsData, setDomainsData] = useState([])
  const [checkedInToday, setCheckedInToday] = useState({})
  const [selectedDomain, setSelectedDomain] = useState(null)
  const [loading, setLoading]       = useState(true)
  const [activeTab, setActiveTab]   = useState(0)
  const [trends, setTrends]         = useState({})
  const toast = useToast()

  useEffect(() => { loadAll() }, [])

  const loadAll = async () => {
    setLoading(true)
    try {
      const [domainsRes, progressRes] = await Promise.all([
        domainsAPI.getDomains(),
        domainsAPI.getAllProgress().catch(() => ({ data: {} })),
      ])
      const domList = domainsRes.data || []
      const prog    = progressRes.data || {}
      setDomains(domList)
      setAllProgress(prog)

      // Load checkins per domain for heatmap
      const checkinResults = await Promise.all(
        domList.map(d => domainsAPI.getDomainCheckins(d.id, 7).catch(() => ({ data: [] })))
      )
      const today = getTodayKey()
      const todayMap = {}
      const fullData = domList.map((d, i) => {
        const checkins = checkinResults[i].data || []
        if (checkins.some(c => c.date === today && c.status === 'completed')) todayMap[d.id] = true
        return { domain: d, checkins }
      })
      setDomainsData(fullData)
      setCheckedInToday(todayMap)

      // Load trend data from radar endpoint
      try {
        const radarRes = await domainsAPI.getRadarData(4)
        const rd = radarRes.data
        if (rd?.series && rd?.live) {
          const t = {}
          DOMAIN_ORDER.forEach(id => {
            const series = rd.series[id] || []
            const prev = [...series].reverse().find(v => v != null)
            t[id] = prev != null ? Math.round((rd.live[id] || 0) - prev) : null
          })
          setTrends(t)
        }
      } catch {}
    } catch {
      toast({ title: 'Could not load domains', status: 'error', duration: 3000 })
    } finally {
      setLoading(false)
    }
  }

  const handleQuickCheckin = async (domainId, alreadyChecked) => {
    if (alreadyChecked) return
    setCheckedInToday(prev => ({ ...prev, [domainId]: true }))
    try {
      await domainsAPI.createCheckin(domainId, 'completed')
      toast({ title: `✅ ${DOMAIN_META[domainId]?.label || domainId} checked in!`, status: 'success', duration: 2000 })
      setAllProgress(prev => ({
        ...prev,
        [domainId]: { ...prev[domainId], weekly_checkins: (prev[domainId]?.weekly_checkins || 0) + 1 }
      }))
    } catch {
      setCheckedInToday(prev => ({ ...prev, [domainId]: false }))
      toast({ title: 'Check-in failed', status: 'error', duration: 2000 })
    }
  }

  if (selectedDomain) {
    return <DomainDetail domain={selectedDomain} onBack={() => setSelectedDomain(null)} />
  }

  return (
    <VStack spacing={6} align="stretch">
      {/* Header */}
      <HStack justify="space-between" flexWrap="wrap" gap={2}>
        <VStack align="start" spacing={0}>
          <Heading size="lg">Life Domains</Heading>
          <Text color="gray.500" fontSize="sm">
            {Object.values(checkedInToday).filter(Boolean).length} of {domains.length} checked in today
          </Text>
        </VStack>
        <HStack>
          <IconButton icon={<FiRefreshCw />} variant="ghost" size="sm" onClick={loadAll} isLoading={loading} aria-label="Refresh" />
          <Button
            size="sm"
            colorScheme="brand"
            variant="outline"
            leftIcon={<FiCheck />}
            onClick={() => domains.forEach(d => !checkedInToday[d.id] && handleQuickCheckin(d.id, false))}
            isDisabled={Object.values(checkedInToday).filter(Boolean).length === domains.length}
          >
            Check In All
          </Button>
        </HStack>
      </HStack>

      {/* Insight bar */}
      {!loading && <InsightBar allProgress={allProgress} />}

      {/* Tabs: Overview / Radar */}
      <Tabs variant="soft-rounded" colorScheme="brand" index={activeTab} onChange={setActiveTab}>
        <TabList>
          <Tab fontSize="sm">📋 Overview</Tab>
          <Tab fontSize="sm">📡 Radar</Tab>
        </TabList>

        <TabPanels>
          {/* Overview tab */}
          <TabPanel px={0} pt={4}>
            <VStack spacing={5} align="stretch">
              {/* Domain cards */}
              {loading ? (
                <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
                  {[0,1,2,3,4,5].map(i => <Card key={i}><CardBody><Skeleton height="200px" /></CardBody></Card>)}
                </SimpleGrid>
              ) : (
                <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
                  {domains.map(domain => (
                    <DomainCard
                      key={domain.id}
                      domain={domain}
                      progress={allProgress[domain.id]}
                      checkedInToday={checkedInToday}
                      trend={trends[domain.id]}
                      onSelect={setSelectedDomain}
                      onQuickCheckin={handleQuickCheckin}
                    />
                  ))}
                </SimpleGrid>
              )}

              {/* Heatmap */}
              {!loading && <WeeklyHeatmap domainsData={domainsData} />}
            </VStack>
          </TabPanel>

          {/* Radar tab */}
          <TabPanel px={0} pt={4}>
            <RadarPanel allProgress={allProgress} />
          </TabPanel>
        </TabPanels>
      </Tabs>
    </VStack>
  )
}

export default Domains
