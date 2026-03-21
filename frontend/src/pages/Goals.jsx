// Busy Bee — Goals Page (v4)
// Drop-in replacement for frontend/src/pages/Goals.jsx
// New in v4: Goal Detail Drawer — slide-in panel with:
//   • Full-width sparkline (expanded, labeled axes)
//   • Inline edit: title, description, category, target date
//   • Progress slider + one-click milestones (25 / 50 / 75 / 100%)
//   • Notes feed — timestamped text notes per goal (stored in localStorage until backend supports it)
//   • Complete / Pause / Delete actions
//   • Confetti fires from drawer too

import { useState, useEffect, useRef, useCallback } from 'react'
import {
  Box, VStack, HStack, Text, Heading, Card, CardBody, SimpleGrid,
  Badge, Button, Input, InputGroup, InputLeftElement, Select,
  IconButton, Menu, MenuButton, MenuList, MenuItem, Modal, ModalOverlay,
  ModalContent, ModalHeader, ModalBody, ModalFooter, ModalCloseButton,
  useDisclosure, useToast, Slider, SliderTrack, SliderFilledTrack, SliderThumb,
  Tabs, TabList, Tab, TabPanels, TabPanel, Skeleton, AlertDialog,
  AlertDialogOverlay, AlertDialogContent, AlertDialogHeader, AlertDialogBody,
  AlertDialogFooter, Textarea, Tag, TagLabel, Tooltip, Drawer, DrawerOverlay,
  DrawerContent, DrawerCloseButton, DrawerHeader, DrawerBody, DrawerFooter,
  Divider, FormLabel, FormControl, Progress,
} from '@chakra-ui/react'
import {
  FiPlus, FiSearch, FiMoreVertical, FiTarget, FiTrash2, FiEdit2,
  FiCheck, FiClock, FiPause, FiPlay, FiRefreshCw, FiTrendingUp,
  FiSend, FiZap,
} from 'react-icons/fi'
import { dashboardAPI, domainsAPI } from '../services/api'

// ─── Constants ─────────────────────────────────────────────────────────────────

const DOMAIN_META = {
  health:        { color: 'green',  hex: '#48BB78', emoji: '🏃', label: 'Health' },
  career:        { color: 'blue',   hex: '#4299E1', emoji: '💼', label: 'Career' },
  mindset:       { color: 'purple', hex: '#9F7AEA', emoji: '🧠', label: 'Mindset' },
  habits:        { color: 'orange', hex: '#ED8936', emoji: '🔄', label: 'Habits' },
  relationships: { color: 'pink',   hex: '#ED64A6', emoji: '👥', label: 'Relationships' },
  finance:       { color: 'yellow', hex: '#ECC94B', emoji: '💰', label: 'Finance' },
}

const DOMAIN_ORDER = ['health', 'career', 'mindset', 'habits', 'relationships', 'finance']
const STATUS_COLOR  = { active: 'green', completed: 'blue', paused: 'gray' }

const ALL_CATEGORIES = [
  'Fitness','Sleep','Nutrition','Medical','Mental Health',
  'Skills','Work','Business','Learning','Networking',
  'Meditation','Gratitude','Journaling','Reading','Self-care',
  'Morning Routine','Evening Routine','Productivity','Wellness',
  'Family','Friends','Partner','Social','Community',
  'Budgeting','Saving','Investing','Income','Debt',
]

// ─── Confetti ──────────────────────────────────────────────────────────────────

const CONFETTI_COLORS = [
  '#F59E0B','#EF4444','#10B981','#3B82F6','#8B5CF6',
  '#EC4899','#F97316','#06B6D4','#84CC16','#FBBF24',
]

function useConfetti() {
  const canvasRef  = useRef(null)
  const rafRef     = useRef(null)
  const particles  = useRef([])

  useEffect(() => {
    const canvas = document.createElement('canvas')
    canvas.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:9999;'
    document.body.appendChild(canvas)
    canvasRef.current = canvas
    const resize = () => { canvas.width = window.innerWidth; canvas.height = window.innerHeight }
    resize()
    window.addEventListener('resize', resize)
    return () => { cancelAnimationFrame(rafRef.current); document.body.removeChild(canvas); window.removeEventListener('resize', resize) }
  }, [])

  const spawnParticle = useCallback((count, opts = {}) => {
    const W = canvasRef.current?.width || window.innerWidth
    const { originX = W / 2, gravity = 0.35, drag = 0.97, ttl = 220 } = opts
    for (let i = 0; i < count; i++) {
      const angle = -Math.PI / 2 + (Math.random() - 0.5) * Math.PI * 0.9
      const speed = 6 + Math.random() * 10
      particles.current.push({
        x: originX + (Math.random() - 0.5) * W * 0.15,
        y: -10,
        vx: Math.cos(angle) * speed, vy: Math.sin(angle) * speed,
        w: 6 + Math.random() * 8, h: 4 + Math.random() * 5,
        rot: Math.random() * Math.PI * 2, rotV: (Math.random() - 0.5) * 0.25,
        color: CONFETTI_COLORS[Math.floor(Math.random() * CONFETTI_COLORS.length)],
        alpha: 1, gravity, drag, ttl, age: 0,
        shape: Math.random() > 0.6 ? 'circle' : 'rect',
      })
    }
  }, [])

  const animate = useCallback(() => {
    const canvas = canvasRef.current; if (!canvas) return
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    particles.current = particles.current.filter(p => p.age < p.ttl && p.alpha > 0.02)
    for (const p of particles.current) {
      p.age++; p.vy += p.gravity; p.vx *= p.drag; p.vy *= p.drag
      p.x += p.vx; p.y += p.vy; p.rot += p.rotV
      p.alpha = 1 - (p.age / p.ttl) ** 1.5
      ctx.save(); ctx.globalAlpha = p.alpha; ctx.fillStyle = p.color
      ctx.translate(p.x, p.y); ctx.rotate(p.rot)
      if (p.shape === 'circle') { ctx.beginPath(); ctx.arc(0, 0, p.w / 2, 0, Math.PI * 2); ctx.fill() }
      else ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h)
      ctx.restore()
    }
    if (particles.current.length > 0) rafRef.current = requestAnimationFrame(animate)
  }, [])

  const fire = useCallback((type = 'goal') => {
    const W = canvasRef.current?.width || window.innerWidth
    if (type === 'goal') {
      spawnParticle(60, { originX: 0,     gravity: 0.4 })
      spawnParticle(60, { originX: W,     gravity: 0.4 })
      spawnParticle(80, { originX: W / 2, gravity: 0.35, ttl: 260 })
    } else if (type === 'streak') {
      for (let i = 0; i < 150; i++) spawnParticle(1, { originX: Math.random() * W, gravity: 0.18, drag: 0.995, ttl: 320 })
    }
    cancelAnimationFrame(rafRef.current)
    rafRef.current = requestAnimationFrame(animate)
  }, [spawnParticle, animate])

  return { fire }
}

// ─── Completion Banner ─────────────────────────────────────────────────────────

function CompletionBanner({ goal, onDone }) {
  useEffect(() => { const t = setTimeout(onDone, 2500); return () => clearTimeout(t) }, [onDone])
  const meta = DOMAIN_META[goal?.domain_id || goal?.domain]
  return (
    <Box position="fixed" inset={0} display="flex" alignItems="center" justifyContent="center" zIndex={9998} pointerEvents="none">
      <Box bg="white" borderRadius="2xl" shadow="2xl" px={10} py={8} textAlign="center" maxW="360px"
        border="2px solid" borderColor={meta ? `${meta.color}.300` : 'brand.300'}
        style={{ animation: 'bbPop 0.35s cubic-bezier(0.34,1.56,0.64,1) forwards' }}>
        <style>{`@keyframes bbPop { from{opacity:0;transform:scale(.6) translateY(30px)} to{opacity:1;transform:scale(1) translateY(0)} }`}</style>
        <Text fontSize="4xl" mb={2}>🎉</Text>
        <Text fontWeight="800" fontSize="xl" color="gray.800">Goal Complete!</Text>
        <Text mt={1} fontSize="sm" color="gray.500" noOfLines={2}>{goal?.title}</Text>
        {meta && <Tag mt={3} colorScheme={meta.color} size="sm" variant="subtle"><TagLabel>{meta.emoji} {meta.label}</TagLabel></Tag>}
      </Box>
    </Box>
  )
}

// ─── Sparkline ─────────────────────────────────────────────────────────────────

function Sparkline({ points, color = '#F59E0B', height = 32, showAxes = false }) {
  const containerRef = useRef(null)
  const [width, setWidth] = useState(200)
  useEffect(() => {
    if (!containerRef.current) return
    const ro = new ResizeObserver(([e]) => setWidth(e.contentRect.width || 200))
    ro.observe(containerRef.current)
    return () => ro.disconnect()
  }, [])

  const hasData = points && points.length >= 2
  const pad = showAxes ? 24 : 4
  const chartH = showAxes ? height - 18 : height

  if (!hasData) {
    return (
      <Box ref={containerRef} w="full">
        <svg width={width} height={height} style={{ display: 'block' }}>
          <line x1={pad} y1={chartH / 2} x2={width - 4} y2={chartH / 2}
            stroke={color} strokeWidth={1.5} strokeDasharray="4 3" opacity={0.35} />
          <text x={width / 2} y={chartH / 2 - 8} textAnchor="middle" fontSize={10} fill="#A0AEC0">No history yet</text>
        </svg>
      </Box>
    )
  }

  const minP   = Math.min(...points.map(p => p.progress))
  const maxP   = Math.max(...points.map(p => p.progress))
  const range  = maxP - minP || 1

  const coords = points.map((p, i) => {
    const x = pad + (i / (points.length - 1)) * (width - pad - 4)
    const y = 4 + ((maxP - p.progress) / range) * (chartH - 8)
    return [x, y, p]
  })

  const polyline   = coords.map(([x, y]) => `${x},${y}`).join(' ')
  const areaPoints = [`${coords[0][0]},${chartH}`, ...coords.map(([x, y]) => `${x},${y}`), `${coords[coords.length - 1][0]},${chartH}`].join(' ')
  const gradId     = `sg_${color.replace(/[^a-zA-Z0-9]/g, '')}_${showAxes ? 'lg' : 'sm'}`
  const [lx, ly]   = coords[coords.length - 1]

  return (
    <Box ref={containerRef} w="full">
      <svg width={width} height={height} style={{ display: 'block', overflow: 'visible' }}>
        <defs>
          <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%"   stopColor={color} stopOpacity={0.3} />
            <stop offset="100%" stopColor={color} stopOpacity={0.02} />
          </linearGradient>
        </defs>

        {/* Grid lines for expanded view */}
        {showAxes && [0, 25, 50, 75, 100].map(lvl => {
          const y = 4 + ((maxP - Math.min(lvl, maxP)) / range) * (chartH - 8)
          if (y < 4 || y > chartH) return null
          return (
            <g key={lvl}>
              <line x1={pad} y1={y} x2={width - 4} y2={y} stroke="#E2E8F0" strokeWidth={1} strokeDasharray="3 2" />
              <text x={pad - 3} y={y + 3} textAnchor="end" fontSize={8} fill="#CBD5E0">{lvl}</text>
            </g>
          )
        })}

        <polygon points={areaPoints} fill={`url(#${gradId})`} />
        <polyline points={polyline} fill="none" stroke={color} strokeWidth={showAxes ? 2.2 : 1.8}
          strokeLinejoin="round" strokeLinecap="round" />

        {/* Dots on every point for expanded view */}
        {showAxes && coords.map(([x, y, p], i) => (
          <Tooltip key={i} label={`${p.progress}%  ${new Date(p.logged_at).toLocaleDateString()}`}>
            <circle cx={x} cy={y} r={3.5} fill={color} stroke="white" strokeWidth={1.5} style={{ cursor: 'default' }} />
          </Tooltip>
        ))}

        {/* End dot for compact view */}
        {!showAxes && <circle cx={lx} cy={ly} r={3} fill={color} />}

        {/* X-axis date labels for expanded view */}
        {showAxes && (() => {
          const step = Math.max(1, Math.floor(coords.length / 5))
          return coords.filter((_, i) => i === 0 || i === coords.length - 1 || i % step === 0).map(([x, , p], i) => (
            <text key={i} x={x} y={height - 2} textAnchor="middle" fontSize={8} fill="#A0AEC0">
              {new Date(p.logged_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
            </text>
          ))
        })()}
      </svg>
    </Box>
  )
}

// ─── Notes (localStorage until backend supports it) ────────────────────────────

function useGoalNotes(goalId) {
  const key = `bb_goal_notes_${goalId}`

  const load = () => {
    try { return JSON.parse(localStorage.getItem(key) || '[]') } catch { return [] }
  }

  const [notes, setNotes] = useState(load)

  const addNote = useCallback((text) => {
    const note = { id: Date.now(), text, createdAt: new Date().toISOString() }
    setNotes(prev => {
      const next = [note, ...prev]
      localStorage.setItem(key, JSON.stringify(next))
      return next
    })
  }, [key])

  const deleteNote = useCallback((id) => {
    setNotes(prev => {
      const next = prev.filter(n => n.id !== id)
      localStorage.setItem(key, JSON.stringify(next))
      return next
    })
  }, [key])

  return { notes, addNote, deleteNote }
}

// ─── Goal Detail Drawer ────────────────────────────────────────────────────────

function GoalDrawer({ goal, isOpen, onClose, onProgressChange, onStatusChange, onDelete, onComplete, onSave }) {
  const [editing, setEditing]     = useState(false)
  const [editTitle, setEditTitle] = useState('')
  const [editDesc, setEditDesc]   = useState('')
  const [editCat, setEditCat]     = useState('')
  const [editDate, setEditDate]   = useState('')
  const [progress, setProgress]   = useState(goal?.progress || 0)
  const [history, setHistory]     = useState(null)
  const [saving, setSaving]       = useState(false)
  const [noteText, setNoteText]   = useState('')
  const { notes, addNote, deleteNote } = useGoalNotes(goal?.id)
  const toast = useToast()

  const domainId = goal?.domain_id || goal?.domain
  const meta     = domainId ? DOMAIN_META[domainId] : null
  const isComplete = goal?.status === 'completed'

  // Sync local progress when goal prop changes
  useEffect(() => { if (goal) setProgress(goal.progress || 0) }, [goal?.id, goal?.progress])

  // Load sparkline history when drawer opens
  useEffect(() => {
    if (!isOpen || !goal?.id || goal.id.startsWith('local_')) { setHistory([]); return }
    setHistory(null)
    domainsAPI.getGoalHistory?.(goal.id)
      .then(r => setHistory(r?.data || []))
      .catch(() => setHistory([]))
  }, [isOpen, goal?.id])

  const startEdit = () => {
    setEditTitle(goal.title)
    setEditDesc(goal.description || '')
    setEditCat(goal.category || '')
    setEditDate(goal.target_date || '')
    setEditing(true)
  }

  const saveEdit = async () => {
    if (!editTitle.trim()) { toast({ title: 'Title required', status: 'warning', duration: 2000 }); return }
    setSaving(true)
    try {
      await domainsAPI.updateGoalFields?.(goal.id, { title: editTitle, description: editDesc, category: editCat, target_date: editDate })
      onSave?.(goal.id, { title: editTitle, description: editDesc, category: editCat, target_date: editDate })
      setEditing(false)
      toast({ title: 'Saved', status: 'success', duration: 1500 })
    } catch {
      toast({ title: 'Could not save', status: 'error', duration: 2000 })
    } finally {
      setSaving(false)
    }
  }

  const handleProgressCommit = async (val) => {
    setSaving(true)
    try {
      await onProgressChange(goal.id, val)
      setHistory(prev => prev ? [...prev, { progress: val, logged_at: new Date().toISOString() }] : prev)
      if (val === 100) { onComplete(goal); onClose() }
    } finally { setSaving(false) }
  }

  const handleMilestone = (val) => { setProgress(val); handleProgressCommit(val) }

  const handleMarkComplete = async () => {
    await onStatusChange(goal.id, 'completed')
    onComplete(goal)
    onClose()
  }

  const handleDeleteConfirm = async () => {
    onDelete(goal.id)
    onClose()
  }

  const submitNote = () => {
    if (!noteText.trim()) return
    addNote(noteText.trim())
    setNoteText('')
  }

  if (!goal) return null

  return (
    <Drawer isOpen={isOpen} onClose={onClose} placement="right" size="md">
      <DrawerOverlay />
      <DrawerContent>
        <DrawerCloseButton />

        {/* Header */}
        <DrawerHeader borderBottomWidth="1px" pb={3}>
          <HStack spacing={3} align="flex-start" pr={8}>
            {meta && <Text fontSize="2xl" mt={0.5}>{meta.emoji}</Text>}
            <VStack align="start" spacing={0.5} flex={1} minW={0}>
              {editing ? (
                <Input
                  value={editTitle} onChange={e => setEditTitle(e.target.value)}
                  fontWeight="700" fontSize="lg" focusBorderColor={`${meta?.color || 'brand'}.400`}
                  autoFocus
                />
              ) : (
                <Text fontWeight="700" fontSize="lg" noOfLines={2} lineHeight="1.3">{goal.title}</Text>
              )}
              <HStack spacing={2} flexWrap="wrap">
                <Badge colorScheme={STATUS_COLOR[goal.status] || 'gray'} fontSize="xs">{goal.status}</Badge>
                {meta && <Tag size="sm" colorScheme={meta.color} variant="subtle"><TagLabel>{meta.label}</TagLabel></Tag>}
                {goal.category && !editing && <Badge variant="outline" fontSize="xs">{goal.category}</Badge>}
              </HStack>
            </VStack>
          </HStack>
        </DrawerHeader>

        <DrawerBody overflowY="auto">
          <VStack spacing={5} align="stretch" py={2}>

            {/* ── Sparkline ── */}
            <Box>
              <HStack justify="space-between" mb={2}>
                <Text fontSize="xs" fontWeight="600" color="gray.500" textTransform="uppercase" letterSpacing="wide">Progress History</Text>
                <Text fontSize="xs" color="gray.400">
                  {history ? `${history.length} data point${history.length !== 1 ? 's' : ''}` : ''}
                </Text>
              </HStack>
              {history === null
                ? <Skeleton height="80px" borderRadius="md" />
                : <Sparkline points={history} color={meta?.hex || '#F59E0B'} height={90} showAxes />
              }
            </Box>

            <Divider />

            {/* ── Progress control ── */}
            <Box>
              <HStack justify="space-between" mb={2}>
                <Text fontSize="xs" fontWeight="600" color="gray.500" textTransform="uppercase" letterSpacing="wide">Progress</Text>
                <Text fontWeight="700" color={meta ? `${meta.color}.600` : 'brand.600'}>{progress}%</Text>
              </HStack>
              <Slider
                value={progress} onChange={setProgress} onChangeEnd={handleProgressCommit}
                min={0} max={100} step={5}
                colorScheme={meta?.color || 'brand'}
                isDisabled={isComplete || saving}
                mb={3}
              >
                <SliderTrack h="6px" borderRadius="full"><SliderFilledTrack /></SliderTrack>
                <SliderThumb boxSize={5} shadow="md" />
              </Slider>

              {/* Milestone buttons */}
              {!isComplete && (
                <HStack spacing={2} flexWrap="wrap">
                  <Text fontSize="xs" color="gray.400">Quick set:</Text>
                  {[25, 50, 75, 100].map(v => (
                    <Button
                      key={v} size="xs"
                      colorScheme={progress >= v ? (meta?.color || 'brand') : 'gray'}
                      variant={progress >= v ? 'solid' : 'outline'}
                      onClick={() => handleMilestone(v)}
                      isDisabled={saving}
                    >
                      {v === 100 ? '🎉 100%' : `${v}%`}
                    </Button>
                  ))}
                </HStack>
              )}
            </Box>

            <Divider />

            {/* ── Details (view / edit) ── */}
            <Box>
              <HStack justify="space-between" mb={3}>
                <Text fontSize="xs" fontWeight="600" color="gray.500" textTransform="uppercase" letterSpacing="wide">Details</Text>
                {!editing
                  ? <Button size="xs" leftIcon={<FiEdit2 size={10} />} variant="ghost" onClick={startEdit}>Edit</Button>
                  : <HStack>
                      <Button size="xs" variant="ghost" onClick={() => setEditing(false)}>Cancel</Button>
                      <Button size="xs" colorScheme={meta?.color || 'brand'} onClick={saveEdit} isLoading={saving}>Save</Button>
                    </HStack>
                }
              </HStack>

              {editing ? (
                <VStack spacing={3} align="stretch">
                  <FormControl>
                    <FormLabel fontSize="xs" color="gray.500">Description</FormLabel>
                    <Textarea value={editDesc} onChange={e => setEditDesc(e.target.value)}
                      focusBorderColor={`${meta?.color || 'brand'}.400`} rows={3} fontSize="sm" />
                  </FormControl>
                  <HStack spacing={3}>
                    <FormControl flex={1}>
                      <FormLabel fontSize="xs" color="gray.500">Category</FormLabel>
                      <Select value={editCat} onChange={e => setEditCat(e.target.value)}
                        focusBorderColor={`${meta?.color || 'brand'}.400`} size="sm">
                        <option value="">None</option>
                        {ALL_CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                      </Select>
                    </FormControl>
                    <FormControl flex={1}>
                      <FormLabel fontSize="xs" color="gray.500">Target Date</FormLabel>
                      <Input type="date" value={editDate} onChange={e => setEditDate(e.target.value)}
                        focusBorderColor={`${meta?.color || 'brand'}.400`} size="sm" />
                    </FormControl>
                  </HStack>
                </VStack>
              ) : (
                <VStack align="stretch" spacing={2}>
                  {goal.description && (
                    <Box bg="gray.50" p={3} borderRadius="md">
                      <Text fontSize="sm" color="gray.700">{goal.description}</Text>
                    </Box>
                  )}
                  <HStack spacing={4} flexWrap="wrap">
                    {goal.category && (
                      <HStack spacing={1}>
                        <Text fontSize="xs" color="gray.400">Category:</Text>
                        <Badge variant="outline" fontSize="xs">{goal.category}</Badge>
                      </HStack>
                    )}
                    {goal.target_date && (
                      <HStack spacing={1}>
                        <FiClock size={11} color="#A0AEC0" />
                        <Text fontSize="xs" color="gray.500">Due {goal.target_date}</Text>
                      </HStack>
                    )}
                    {goal.created_at && (
                      <HStack spacing={1}>
                        <Text fontSize="xs" color="gray.400">
                          Created {new Date(goal.created_at).toLocaleDateString()}
                        </Text>
                      </HStack>
                    )}
                  </HStack>
                  {!goal.description && !goal.category && !goal.target_date && (
                    <Button size="xs" variant="ghost" leftIcon={<FiEdit2 size={10} />} onClick={startEdit} alignSelf="flex-start">
                      Add details
                    </Button>
                  )}
                </VStack>
              )}
            </Box>

            <Divider />

            {/* ── Notes ── */}
            <Box>
              <Text fontSize="xs" fontWeight="600" color="gray.500" textTransform="uppercase" letterSpacing="wide" mb={3}>
                Notes
              </Text>

              {/* Input */}
              <HStack mb={3} align="flex-end">
                <Textarea
                  value={noteText}
                  onChange={e => setNoteText(e.target.value)}
                  placeholder="Add a note…"
                  rows={2}
                  fontSize="sm"
                  focusBorderColor={`${meta?.color || 'brand'}.400`}
                  onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submitNote() } }}
                  flex={1}
                />
                <IconButton
                  icon={<FiSend />}
                  colorScheme={meta?.color || 'brand'}
                  size="sm"
                  onClick={submitNote}
                  isDisabled={!noteText.trim()}
                  aria-label="Add note"
                  alignSelf="flex-end"
                />
              </HStack>

              {/* Feed */}
              {notes.length === 0 ? (
                <Text fontSize="xs" color="gray.400" textAlign="center" py={3}>No notes yet. Jot something down.</Text>
              ) : (
                <VStack spacing={2} align="stretch">
                  {notes.map(note => (
                    <Box key={note.id} bg="gray.50" borderRadius="md" p={3} position="relative" _hover={{ bg: 'gray.100' }}>
                      <Text fontSize="sm" color="gray.700" whiteSpace="pre-wrap">{note.text}</Text>
                      <HStack justify="space-between" mt={1}>
                        <Text fontSize="xs" color="gray.400">
                          {new Date(note.createdAt).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })}
                        </Text>
                        <IconButton
                          icon={<FiTrash2 size={11} />}
                          size="xs" variant="ghost" colorScheme="red"
                          onClick={() => deleteNote(note.id)}
                          aria-label="Delete note"
                        />
                      </HStack>
                    </Box>
                  ))}
                </VStack>
              )}
            </Box>

          </VStack>
        </DrawerBody>

        {/* Footer actions */}
        <DrawerFooter borderTopWidth="1px" gap={2} flexWrap="wrap">
          {!isComplete && (
            <>
              <Button
                size="sm"
                colorScheme={goal.status === 'active' ? 'orange' : 'green'}
                variant="outline"
                leftIcon={goal.status === 'active' ? <FiPause size={13} /> : <FiPlay size={13} />}
                onClick={() => onStatusChange(goal.id, goal.status === 'active' ? 'paused' : 'active')}
              >
                {goal.status === 'active' ? 'Pause' : 'Resume'}
              </Button>
              <Button
                size="sm" colorScheme="green" leftIcon={<FiCheck size={13} />}
                onClick={handleMarkComplete}
              >
                Complete
              </Button>
            </>
          )}
          <Button
            size="sm" colorScheme="red" variant="ghost" leftIcon={<FiTrash2 size={13} />}
            onClick={handleDeleteConfirm} ml="auto"
          >
            Delete
          </Button>
        </DrawerFooter>
      </DrawerContent>
    </Drawer>
  )
}

// ─── New Goal Modal ─────────────────────────────────────────────────────────────

function NewGoalModal({ isOpen, onClose, defaultDomain, onCreated }) {
  const [title, setTitle]             = useState('')
  const [description, setDescription] = useState('')
  const [domain, setDomain]           = useState(defaultDomain || '')
  const [category, setCategory]       = useState('')
  const [targetDate, setTargetDate]   = useState('')
  const [saving, setSaving]           = useState(false)
  const toast = useToast()
  const meta = DOMAIN_META[domain] || { color: 'brand', hex: '#F59E0B' }

  const handleSubmit = async () => {
    if (!title.trim()) { toast({ title: 'Add a title', status: 'warning', duration: 2000 }); return }
    setSaving(true)
    try {
      let newGoal
      if (domain && domainsAPI.createGoal) {
        const res = await domainsAPI.createGoal(domain, title, description, category, targetDate)
        newGoal = res?.data
      }
      newGoal = newGoal || {
        id: `local_${Date.now()}`, domain_id: domain, title, description,
        category: category || 'General', progress: 0, status: 'active',
        target_date: targetDate || null, created_at: new Date().toISOString(),
      }
      onCreated(newGoal, domain)
      toast({ title: '🎯 Goal created!', status: 'success', duration: 2000 })
      setTitle(''); setDescription(''); setCategory(''); setTargetDate(''); setDomain(defaultDomain || '')
      onClose()
    } catch (err) {
      toast({ title: 'Could not save goal', description: err.message, status: 'error', duration: 3000 })
    } finally { setSaving(false) }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="md">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>New Goal</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <VStack spacing={4}>
            <Input placeholder="What's your goal?" value={title} onChange={e => setTitle(e.target.value)} focusBorderColor={`${meta.color}.400`} autoFocus />
            <Textarea placeholder="Description (optional)" value={description} onChange={e => setDescription(e.target.value)} focusBorderColor={`${meta.color}.400`} rows={2} />
            <HStack w="full" spacing={3}>
              <Select placeholder="Life domain" value={domain} onChange={e => setDomain(e.target.value)}>
                {DOMAIN_ORDER.map(id => <option key={id} value={id}>{DOMAIN_META[id].emoji} {DOMAIN_META[id].label}</option>)}
              </Select>
              <Input type="date" value={targetDate} onChange={e => setTargetDate(e.target.value)} focusBorderColor="brand.400" />
            </HStack>
            {domain && (
              <Select placeholder="Category (optional)" value={category} onChange={e => setCategory(e.target.value)} focusBorderColor={`${meta.color}.400`}>
                {ALL_CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
              </Select>
            )}
          </VStack>
        </ModalBody>
        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose}>Cancel</Button>
          <Button colorScheme="brand" onClick={handleSubmit} isLoading={saving} leftIcon={<FiTarget />}>Create Goal</Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}

// ─── Goal Card ─────────────────────────────────────────────────────────────────

function GoalCard({ goal, onProgressChange, onStatusChange, onDelete, onComplete, onOpenDrawer }) {
  const [progress, setProgress] = useState(goal.progress || 0)
  const [saving, setSaving]     = useState(false)
  const [history, setHistory]   = useState(null)
  const { isOpen: isDeleteOpen, onOpen: onDeleteOpen, onClose: onDeleteClose } = useDisclosure()

  const domainId  = goal.domain_id || goal.domain
  const meta      = domainId ? DOMAIN_META[domainId] : null
  const lineColor = meta?.hex || '#F59E0B'
  const isComplete = goal.status === 'completed'

  useEffect(() => {
    if (!goal.id || goal.id.startsWith('local_')) { setHistory([]); return }
    domainsAPI.getGoalHistory?.(goal.id).then(r => setHistory(r?.data || [])).catch(() => setHistory([]))
  }, [goal.id])

  // Sync if parent updates
  useEffect(() => { setProgress(goal.progress || 0) }, [goal.progress])

  const handleProgressCommit = async (val) => {
    setSaving(true)
    try {
      await onProgressChange(goal.id, val)
      setHistory(prev => prev ? [...prev, { progress: val, logged_at: new Date().toISOString() }] : prev)
      if (val === 100) onComplete(goal)
    } finally { setSaving(false) }
  }

  const trend = history && history.length >= 2
    ? history[history.length - 1].progress - history[0].progress : null

  return (
    <>
      <Card
        borderLeft="3px solid"
        borderLeftColor={meta ? `${meta.color}.400` : 'gray.200'}
        opacity={isComplete ? 0.75 : 1}
        _hover={{ shadow: isComplete ? 'sm' : 'md', cursor: 'pointer' }}
        transition="all 0.15s"
        onClick={() => onOpenDrawer(goal)}
        position="relative" overflow="hidden"
      >
        {isComplete && (
          <Box position="absolute" inset={0} pointerEvents="none"
            bgGradient={`linear(135deg, ${meta?.hex || '#F59E0B'}10 0%, transparent 60%)`} />
        )}
        <CardBody>
          <HStack justify="space-between" mb={1} align="flex-start">
            <VStack align="start" spacing={0} flex={1} minW={0}>
              <HStack spacing={1}>
                {isComplete && <Text fontSize="sm">✅</Text>}
                <Text fontWeight="600" noOfLines={2} lineHeight="1.3"
                  textDecoration={isComplete ? 'line-through' : 'none'}
                  color={isComplete ? 'gray.400' : 'inherit'}>{goal.title}</Text>
              </HStack>
              {goal.description && <Text fontSize="xs" color="gray.500" noOfLines={1}>{goal.description}</Text>}
            </VStack>
            <Menu>
              <MenuButton as={IconButton} icon={<FiMoreVertical />} variant="ghost" size="sm" flexShrink={0}
                onClick={e => e.stopPropagation()} />
              <MenuList onClick={e => e.stopPropagation()}>
                <MenuItem icon={<FiEdit2 />} onClick={() => onOpenDrawer(goal)}>Open Details</MenuItem>
                <MenuItem icon={goal.status === 'active' ? <FiPause /> : <FiPlay />}
                  onClick={() => onStatusChange(goal.id, goal.status === 'active' ? 'paused' : 'active')}>
                  {goal.status === 'active' ? 'Pause' : 'Resume'}
                </MenuItem>
                {!isComplete && (
                  <MenuItem icon={<FiCheck />} onClick={() => { onStatusChange(goal.id, 'completed'); onComplete(goal) }}>
                    Mark Complete
                  </MenuItem>
                )}
                <MenuItem icon={<FiTrash2 />} color="red.500" onClick={onDeleteOpen}>Delete</MenuItem>
              </MenuList>
            </Menu>
          </HStack>

          <HStack spacing={2} mb={3} flexWrap="wrap">
            <Badge colorScheme={STATUS_COLOR[goal.status] || 'gray'} fontSize="xs">{goal.status}</Badge>
            {meta && <Tag size="sm" colorScheme={meta.color} variant="subtle"><TagLabel>{meta.emoji} {meta.label}</TagLabel></Tag>}
            {goal.category && <Badge variant="outline" fontSize="xs">{goal.category}</Badge>}
            {goal.target_date && (
              <HStack spacing={1} fontSize="xs" color="gray.400">
                <FiClock size={10} /><Text>{goal.target_date}</Text>
              </HStack>
            )}
          </HStack>

          {/* Sparkline + trend */}
          <HStack justify="space-between" align="flex-end" mb={2}>
            <Box flex={1}>
              {history === null
                ? <Skeleton height="32px" borderRadius="sm" />
                : <Sparkline points={history.length ? history : [{ progress, logged_at: new Date().toISOString() }]} color={lineColor} height={32} />
              }
            </Box>
            {trend !== null && (
              <Tooltip label={`${trend > 0 ? '+' : ''}${trend}% since start`} placement="top">
                <HStack spacing={1} fontSize="xs" fontWeight="bold" flexShrink={0} ml={2}
                  color={trend > 0 ? 'green.500' : trend < 0 ? 'red.400' : 'gray.400'}>
                  <FiTrendingUp size={12} /><Text>{trend > 0 ? '+' : ''}{trend}%</Text>
                </HStack>
              </Tooltip>
            )}
          </HStack>

          {/* Progress slider */}
          <VStack spacing={1} align="stretch" onClick={e => e.stopPropagation()}>
            <HStack justify="space-between">
              <Text fontSize="xs" color="gray.500">Progress</Text>
              <Text fontSize="xs" fontWeight="bold" color={meta ? `${meta.color}.600` : 'brand.600'}>{progress}%</Text>
            </HStack>
            <Tooltip label={isComplete ? 'Already complete' : 'Drag or click card for details'} placement="top">
              <Slider value={progress} onChange={setProgress} onChangeEnd={handleProgressCommit}
                min={0} max={100} step={5} colorScheme={meta?.color || 'brand'} isDisabled={isComplete || saving}>
                <SliderTrack><SliderFilledTrack /></SliderTrack>
                <SliderThumb boxSize={4} />
              </Slider>
            </Tooltip>
          </VStack>
        </CardBody>
      </Card>

      <AlertDialog isOpen={isDeleteOpen} leastDestructiveRef={useRef()} onClose={onDeleteClose}>
        <AlertDialogOverlay>
          <AlertDialogContent>
            <AlertDialogHeader>Delete Goal</AlertDialogHeader>
            <AlertDialogBody>Delete <strong>{goal.title}</strong>? This can't be undone.</AlertDialogBody>
            <AlertDialogFooter>
              <Button onClick={onDeleteClose}>Cancel</Button>
              <Button colorScheme="red" ml={3} onClick={() => { onDelete(goal.id); onDeleteClose() }}>Delete</Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>
    </>
  )
}

// ─── Main Goals Page ───────────────────────────────────────────────────────────

function Goals() {
  const [allGoals, setAllGoals]           = useState([])
  const [loading, setLoading]             = useState(true)
  const [statusFilter, setStatusFilter]   = useState('all')
  const [search, setSearch]               = useState('')
  const [activeDomain, setActiveDomain]   = useState('all')
  const [completedGoal, setCompletedGoal] = useState(null)
  const [drawerGoal, setDrawerGoal]       = useState(null)
  const { isOpen: isNewOpen, onOpen: onNewOpen, onClose: onNewClose } = useDisclosure()
  const { isOpen: isDrawerOpen, onOpen: onDrawerOpen, onClose: onDrawerClose } = useDisclosure()
  const toast = useToast()
  const { fire: fireConfetti } = useConfetti()

  useEffect(() => { loadGoals() }, [])

  const loadGoals = async () => {
    setLoading(true)
    try {
      const [dashRes, ...domRes] = await Promise.all([
        dashboardAPI.getGoals().catch(() => ({ data: { goals: [] } })),
        ...DOMAIN_ORDER.map(id => domainsAPI.getDomainGoals(id).catch(() => ({ data: [] }))),
      ])
      const dashGoals   = dashRes.data?.goals || []
      const domainGoals = []
      DOMAIN_ORDER.forEach((id, i) => {
        ;(domRes[i].data || []).forEach(g => {
          if (!domainGoals.find(x => x.id === g.id)) domainGoals.push({ ...g, domain_id: id })
        })
      })
      const seen = new Set()
      setAllGoals([...dashGoals, ...domainGoals].filter(g => { if (seen.has(g.id)) return false; seen.add(g.id); return true }))
    } catch {
      toast({ title: 'Could not load goals', status: 'error', duration: 3000 })
    } finally { setLoading(false) }
  }

  const handleGoalComplete = useCallback((goal) => { fireConfetti('goal'); setCompletedGoal(goal) }, [fireConfetti])

  const handleGoalCreated = (goal, domainId) => {
    setAllGoals(prev => [{ ...goal, domain_id: domainId || goal.domain_id }, ...prev])
  }

  const handleProgressChange = async (goalId, progress) => {
    setAllGoals(prev => prev.map(g => g.id === goalId ? { ...g, progress, status: progress === 100 ? 'completed' : g.status } : g))
    setDrawerGoal(prev => prev?.id === goalId ? { ...prev, progress, status: progress === 100 ? 'completed' : prev.status } : prev)
    try { await (domainsAPI.updateGoal?.(goalId, progress) ?? dashboardAPI.updateGoal?.(goalId, progress)) }
    catch { toast({ title: 'Could not save progress', status: 'error', duration: 2000 }) }
  }

  const handleStatusChange = async (goalId, status) => {
    setAllGoals(prev => prev.map(g => g.id === goalId ? { ...g, status } : g))
    setDrawerGoal(prev => prev?.id === goalId ? { ...prev, status } : prev)
    try { await domainsAPI.updateGoalStatus?.(goalId, status) } catch {}
  }

  const handleDelete = async (goalId) => {
    setAllGoals(prev => prev.filter(g => g.id !== goalId))
    try { await domainsAPI.deleteGoal?.(goalId); toast({ title: 'Goal deleted', status: 'info', duration: 2000 }) } catch {}
  }

  const handleSave = (goalId, fields) => {
    setAllGoals(prev => prev.map(g => g.id === goalId ? { ...g, ...fields } : g))
    setDrawerGoal(prev => prev?.id === goalId ? { ...prev, ...fields } : prev)
  }

  const openDrawer = (goal) => { setDrawerGoal(goal); onDrawerOpen() }

  const filtered = allGoals.filter(g => {
    if (statusFilter !== 'all' && g.status !== statusFilter) return false
    if (activeDomain !== 'all' && g.domain_id !== activeDomain) return false
    if (search && !g.title.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  const domainCounts = Object.fromEntries(DOMAIN_ORDER.map(id => [id, allGoals.filter(g => g.domain_id === id).length]))

  return (
    <VStack spacing={6} align="stretch">
      {completedGoal && <CompletionBanner goal={completedGoal} onDone={() => setCompletedGoal(null)} />}

      {/* Drawer */}
      <GoalDrawer
        goal={drawerGoal}
        isOpen={isDrawerOpen}
        onClose={onDrawerClose}
        onProgressChange={handleProgressChange}
        onStatusChange={handleStatusChange}
        onDelete={handleDelete}
        onComplete={handleGoalComplete}
        onSave={handleSave}
      />

      {/* Header */}
      <HStack justify="space-between" flexWrap="wrap" gap={2}>
        <VStack align="start" spacing={0}>
          <Heading size="lg">Goals</Heading>
          <Text color="gray.500" fontSize="sm">
            {allGoals.length} total · {allGoals.filter(g => g.status === 'active').length} active · {allGoals.filter(g => g.status === 'completed').length} completed
          </Text>
        </VStack>
        <HStack>
          <IconButton icon={<FiRefreshCw />} variant="ghost" size="sm" onClick={loadGoals} isLoading={loading} aria-label="Refresh" />
          <Button leftIcon={<FiPlus />} colorScheme="brand" onClick={onNewOpen}>New Goal</Button>
        </HStack>
      </HStack>

      {/* Domain tabs */}
      <Tabs variant="soft-rounded" colorScheme="brand" onChange={i => setActiveDomain(i === 0 ? 'all' : DOMAIN_ORDER[i - 1])}>
        <TabList overflowX="auto" pb={1} css={{ '&::-webkit-scrollbar': { display: 'none' } }}>
          <Tab fontSize="sm" whiteSpace="nowrap">All <Badge ml={1} colorScheme="gray">{allGoals.length}</Badge></Tab>
          {DOMAIN_ORDER.map(id => {
            const m = DOMAIN_META[id]
            return (
              <Tab key={id} fontSize="sm" whiteSpace="nowrap">
                {m.emoji} {m.label}
                {domainCounts[id] > 0 && <Badge ml={1} colorScheme={m.color}>{domainCounts[id]}</Badge>}
              </Tab>
            )
          })}
        </TabList>

        <TabPanels>
          {['all', ...DOMAIN_ORDER].map(domainKey => (
            <TabPanel key={domainKey} px={0} pt={4}>
              <HStack mb={4} flexWrap="wrap" gap={2}>
                <InputGroup maxW="280px">
                  <InputLeftElement><FiSearch color="gray" /></InputLeftElement>
                  <Input placeholder="Search goals…" value={search} onChange={e => setSearch(e.target.value)} bg="white" />
                </InputGroup>
                <Select maxW="140px" value={statusFilter} onChange={e => setStatusFilter(e.target.value)} bg="white">
                  <option value="all">All Status</option>
                  <option value="active">Active</option>
                  <option value="completed">Completed</option>
                  <option value="paused">Paused</option>
                </Select>
              </HStack>

              {loading ? (
                <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
                  {[0,1,2,3,4,5].map(i => <Card key={i}><CardBody><Skeleton height="200px" /></CardBody></Card>)}
                </SimpleGrid>
              ) : filtered.length === 0 ? (
                <Card><CardBody textAlign="center" py={12}>
                  <Text fontSize="3xl">🎯</Text>
                  <Text mt={3} color="gray.500">{search ? `No goals matching "${search}"` : 'No goals yet.'}</Text>
                  <Button mt={4} size="sm" colorScheme="brand" leftIcon={<FiPlus />} onClick={onNewOpen}>Create a goal</Button>
                </CardBody></Card>
              ) : (
                <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
                  {filtered.map(goal => (
                    <GoalCard
                      key={goal.id} goal={goal}
                      onProgressChange={handleProgressChange}
                      onStatusChange={handleStatusChange}
                      onDelete={handleDelete}
                      onComplete={handleGoalComplete}
                      onOpenDrawer={openDrawer}
                    />
                  ))}
                </SimpleGrid>
              )}
            </TabPanel>
          ))}
        </TabPanels>
      </Tabs>

      <NewGoalModal
        isOpen={isNewOpen} onClose={onNewClose}
        defaultDomain={activeDomain !== 'all' ? activeDomain : ''}
        onCreated={handleGoalCreated}
      />
    </VStack>
  )
}

export default Goals
