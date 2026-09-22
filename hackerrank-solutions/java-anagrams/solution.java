

    static boolean isAnagram(String a, String b) {
        // Complete the function
        a=a.toLowerCase(); 
        b=b.toLowerCase(); 
        if(a.length() != b.length()) 
        return false; 
        char[] str1=a.toCharArray(); 
        char[] str2=b.toCharArray(); 
        java.util.Arrays.sort(str1); 
        java.util.Arrays.sort(str2); 
        return java.util.Arrays.equals(str1,str2);
    }
