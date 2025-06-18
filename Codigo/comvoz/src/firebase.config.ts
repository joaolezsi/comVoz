// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyDcCjqu_Kzw9r9Kz0Pgg0cIGjNbHzz8BNs",
  authDomain: "comvoz-3fe5b.firebaseapp.com",
  projectId: "comvoz-3fe5b",
  storageBucket: "comvoz-3fe5b.firebasestorage.app",
  messagingSenderId: "111200093772",
  appId: "1:111200093772:web:a534ecd1f6c6abb071d6e9",
  measurementId: "G-9JQFQ4Q645"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

export { app, analytics, firebaseConfig }; 