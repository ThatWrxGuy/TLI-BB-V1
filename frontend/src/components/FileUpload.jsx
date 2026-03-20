import { useState, useRef } from 'react'
import { Box, VStack, HStack, Text, Button, Icon, Table, Thead, Tbody, Tr, Th, Td, Badge, useToast } from '@chakra-ui/react'
import { FiUpload, FiFile, FiTrash2, FiDownload } from 'react-icons/fi'

const ALLOWED_TYPES = {
  document: ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
  spreadsheet: ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
  text: ['text/plain', 'text/csv'],
}

const CATEGORIES = [
  { value: 'resume', label: 'Resume' },
  { value: 'certificate', label: 'Certificate' },
  { value: 'tax', label: 'Tax Document' },
  { value: 'invoice', label: 'Invoice' },
  { value: 'other', label: 'Other' },
]

function FileUpload({ onUploadComplete }) {
  const [files, setFiles] = useState([])
  const [loading, setLoading] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState('other')
  const inputRef = useRef(null)
  const toast = useToast()

  const handleFileChange = async (e) => {
    const selectedFiles = Array.from(e.target.files || [])
    if (selectedFiles.length === 0) return

    // Validate each file
    for (const file of selectedFiles) {
      const isValid = Object.values(ALLOWED_TYPES).flat().includes(file.type)
      if (!isValid) {
        toast({
          title: 'Invalid file type',
          description: `${file.name} is not allowed`,
          status: 'error',
          duration: 3000,
        })
        return
      }

      if (file.size > 10 * 1024 * 1024) {
        toast({
          title: 'File too large',
          description: `${file.name} exceeds 10MB limit`,
          status: 'error',
          duration: 3000,
        })
        return
      }
    }

    setLoading(true)
    
    // Simulate upload
    await new Promise(r => setTimeout(r, 1500))

    const newFiles = selectedFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: file.size,
      type: file.type,
      category: selectedCategory,
      uploadedAt: new Date().toISOString(),
      url: URL.createObjectURL(file),
    }))

    setFiles(prev => [...prev, ...newFiles])
    setLoading(false)

    toast({
      title: 'Files uploaded',
      description: `${selectedFiles.length} file(s) uploaded successfully`,
      status: 'success',
      duration: 3000,
    })

    if (onUploadComplete) {
      onUploadComplete(newFiles)
    }
  }

  const handleDelete = (fileId) => {
    setFiles(prev => prev.filter(f => f.id !== fileId))
  }

  const formatSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  const getCategoryBadge = (category) => {
    const colors = {
      resume: 'blue',
      certificate: 'green',
      tax: 'orange',
      invoice: 'purple',
      other: 'gray',
    }
    return colors[category] || 'gray'
  }

  return (
    <VStack spacing={4} align="stretch">
      {/* Upload Area */}
      <Box
        border="2px dashed"
        borderColor="gray.200"
        borderRadius="xl"
        p={8}
        textAlign="center"
        cursor="pointer"
        _hover={{ borderColor: 'brand.500', bg: 'brand.50' }}
        transition="all 0.2s"
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          multiple
          accept=".pdf,.doc,.docx,.xls,.xlsx,.txt,.csv"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        
        <VStack spacing={2}>
          <Icon as={FiUpload} boxSize={8} color="gray.400" />
          <Text fontWeight="500" color="gray.600">
            Drop files here or click to upload
          </Text>
          <Text fontSize="sm" color="gray.500">
            PDF, Word, Excel, CSV. Max 10MB each.
          </Text>
        </VStack>
      </Box>

      {/* File List */}
      {files.length > 0 && (
        <Box>
          <Text fontWeight="600" mb={3}>
            Uploaded Files ({files.length})
          </Text>
          <Table variant="simple" size="sm">
            <Thead>
              <Tr>
                <Th>Name</Th>
                <Th>Size</Th>
                <Th>Category</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {files.map(file => (
                <Tr key={file.id}>
                  <Td>
                    <HStack>
                      <Icon as={FiFile} color="gray.400" />
                      <Text noOfLines={1} maxW="200px">{file.name}</Text>
                    </HStack>
                  </Td>
                  <Td>{formatSize(file.size)}</Td>
                  <Td>
                    <Badge colorScheme={getCategoryBadge(file.category)}>
                      {file.category}
                    </Badge>
                  </Td>
                  <Td>
                    <HStack spacing={2}>
                      <Button
                        size="xs"
                        variant="ghost"
                        leftIcon={<FiDownload />}
                        onClick={() => window.open(file.url)}
                      >
                        Download
                      </Button>
                      <Button
                        size="xs"
                        variant="ghost"
                        colorScheme="red"
                        leftIcon={<FiTrash2 />}
                        onClick={() => handleDelete(file.id)}
                      >
                        Delete
                      </Button>
                    </HStack>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Box>
      )}
    </VStack>
  )
}

export default FileUpload
