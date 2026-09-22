import java.io.*;
import java.util.*;

public class Solution {

    public static void main(String[] args) {
        
        Scanner sc=new Scanner(System.in);
        String A=sc.next();
        String rev="";
        /* Enter your code here. Print output to STDOUT. */
        for(int i=0;i<A.length();i++){
            char ch=A.charAt(i);
            rev=ch+rev;
        }
        if(rev.compareTo(A)==0){
            System.out.println("Yes");
        }
        else{
            System.out.println("No");
        }
        
    }
}
