import React, { useState } from 'react';
import { Formik, Form } from 'formik';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Link,
  Alert,
  CircularProgress,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { passwordResetValidationSchema } from '../../utils/validation';
import axios from 'axios';

const ForgotPasswordPage: React.FC = () => {
  const [successMessage, setSuccessMessage] = useState('');
  const navigate = useNavigate();

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 8, mb: 4 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom align="center">
            Reset Password
          </Typography>

          {successMessage && (
            <Alert severity="success" sx={{ mb: 2 }}>
              {successMessage}
            </Alert>
          )}

          <Formik
            initialValues={{ email: '' }}
            validationSchema={passwordResetValidationSchema}
            onSubmit={async (values, { setSubmitting, setErrors }) => {
              try {
                await axios.post('http://localhost:8000/auth/reset-password', values);
                setSuccessMessage('Password reset instructions sent to your email');
                setTimeout(() => navigate('/login'), 3000);
              } catch (err) {
                setErrors({ email: 'Failed to send reset instructions' });
              } finally {
                setSubmitting(false);
              }
            }}
          >
            {({ values, errors, touched, handleChange, handleBlur, isSubmitting }) => (
              <Form>
                <TextField
                  fullWidth
                  id="email"
                  name="email"
                  label="Email"
                  type="email"
                  value={values.email}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  error={touched.email && Boolean(errors.email)}
                  helperText={touched.email && errors.email}
                  margin="normal"
                  required
                  autoFocus
                />

                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  size="large"
                  disabled={isSubmitting}
                  sx={{ mt: 3, mb: 2 }}
                >
                  {isSubmitting ? (
                    <CircularProgress size={24} color="inherit" />
                  ) : (
                    'Send Reset Instructions'
                  )}
                </Button>
              </Form>
            )}
          </Formik>

          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <Link href="/login" variant="body2">
              Back to Sign In
            </Link>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default ForgotPasswordPage;
