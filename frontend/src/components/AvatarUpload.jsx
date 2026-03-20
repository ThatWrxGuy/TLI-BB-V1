import { useState, useRef } from 'react'
import { Box, VStack, HStack, Text, Button, Avatar, Input, Image, useToast } from '@chakra-ui/react'
import { FiUpload, FiCamera } from 'react-icons/fi'
import { uploadAPI } from '../services/api'

function AvatarUpload({ currentAvatar, onUploadComplete }) {
  const [loading, setLoading] = useState(false)
  const [preview, setPreview] = useState(null)
  const inputRef = useRef(null)
  const toast = useToast()

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file type
    if (!file.type.startsWith('image/')) {
      toast({
        title: 'Invalid file type',
        description: 'Please select an image file',
        status: 'error',
        duration: 3000,
      })
      return
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      toast({
        title: 'File too large',
        description: 'Maximum file size is 5MB',
        status: 'error',
        duration: 3000,
      })
      return
    }

    // Create preview
    const reader = new FileReader()
    reader.onload = (e) => setPreview(e.target.result)
    reader.readAsDataURL(file)

    // Upload
    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      // For demo, we'll simulate upload
      await new Promise(r => setTimeout(r, 1000))
      
      toast({
        title: 'Avatar updated',
        status: 'success',
        duration: 3000,
      })
      
      if (onUploadComplete) {
        onUploadComplete(URL.createObjectURL(file))
      }
    } catch (err) {
      toast({
        title: 'Upload failed',
        description: 'Please try again',
        status: 'error',
        duration: 3000,
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <VStack spacing={4}>
      <Box position="relative">
        <Avatar
          size="2xl"
          src={preview || currentAvatar}
          name="User"
          bg="brand.500"
        >
          {preview && (
            <Box
              position="absolute"
              bottom={0}
              right={0}
              bg="brand.500"
              borderRadius="full"
              p={2}
            >
              <FiCamera color="white" />
            </Box>
          )}
        </Avatar>
        
        <Input
          ref={inputRef}
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          display="none"
        />
      </Box>

      <Button
        leftIcon={<FiUpload />}
        onClick={() => inputRef.current?.click()}
        isLoading={loading}
        loadingText="Uploading..."
        variant="outline"
        size="sm"
      >
        {currentAvatar ? 'Change Avatar' : 'Upload Avatar'}
      </Button>

      <Text fontSize="xs" color="gray.500">
        JPG, PNG, GIF. Max 5MB.
      </Text>
    </VStack>
  )
}

export default AvatarUpload
