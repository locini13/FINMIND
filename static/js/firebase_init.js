import { initializeApp } from "https://www.gstatic.com/firebasejs/9.6.1/firebase-app.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/9.6.1/firebase-firestore.js";
// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyCH_IbeBzHjFAUS5rWYRGA5Aw9VrgE8RmU",
  authDomain: "final-61790.firebaseapp.com",
  projectId: "final-61790",
  storageBucket: "final-61790.appspot.com",  // typically appspot.com
  messagingSenderId: "523709558384",
  appId: "1:523709558384:web:d662009ccbd5be1447ceb5"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
export const db = getFirestore(app);
