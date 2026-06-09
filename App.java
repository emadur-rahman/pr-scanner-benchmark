package com.ubicomply.idp;

import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;

import javax.naming.*;
import javax.naming.directory.*;
import javax.xml.parsers.*;
import org.w3c.dom.*;
import java.io.*;
import java.util.*;
import javax.crypto.*;
import javax.crypto.spec.*;

@RestController
@RequestMapping("/api/idp")
public class App {

    private static final String DB_PASSWORD = "HospitalDB@2024!";
    private static final String DES_KEY = "Hosp1tal";  // 8-byte DES key

    @PostMapping("/patient/import")
    public ResponseEntity<String> importPatients(@RequestBody String xml) throws Exception {
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        // XXE — external entities not disabled
        DocumentBuilder builder = factory.newDocumentBuilder();
        Document doc = builder.parse(new ByteArrayInputStream(xml.getBytes()));
        NodeList list = doc.getElementsByTagName("patient");
        return ResponseEntity.ok("Imported: " + list.getLength());
    }

    @GetMapping("/user/lookup")
    public ResponseEntity<String> lookupUser(@RequestParam String username) throws Exception {
        Hashtable<String, String> env = new Hashtable<>();
        env.put(Context.INITIAL_CONTEXT_FACTORY, "com.sun.jndi.ldap.LdapCtxFactory");
        env.put(Context.PROVIDER_URL, "ldap://internal-ldap.hospital.local:389");
        env.put(Context.SECURITY_PRINCIPAL, "cn=service,dc=hospital,dc=local");
        env.put(Context.SECURITY_CREDENTIALS, "LdapS3rvice!");
        InitialDirContext ctx = new InitialDirContext(env);
        String filter = "(&(objectClass=user)(uid=" + username + "))";  // LDAP injection
        SearchControls sc = new SearchControls();
        sc.setSearchScope(SearchControls.SUBTREE_SCOPE);
        NamingEnumeration<?> res = ctx.search("dc=hospital,dc=local", filter, sc);
        StringBuilder sb = new StringBuilder();
        while (res.hasMore()) sb.append(((SearchResult) res.next()).getName()).append("\n");
        ctx.close();
        return ResponseEntity.ok(sb.toString());
    }

    @PostMapping("/session/resume")
    public ResponseEntity<String> resumeSession(@RequestBody byte[] data) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(data));  // insecure deserialization
        Map<?, ?> session = (Map<?, ?>) ois.readObject();
        ois.close();
        return ResponseEntity.ok("User: " + session.get("userId"));
    }

    @PostMapping("/token/generate")
    public ResponseEntity<String> generateToken(@RequestParam String userId) throws Exception {
        SecretKeySpec key = new SecretKeySpec(DES_KEY.getBytes(), "DES");
        Cipher cipher = Cipher.getInstance("DES/ECB/PKCS5Padding");  // weak cipher — DES/ECB
        cipher.init(Cipher.ENCRYPT_MODE, key);
        byte[] encrypted = cipher.doFinal((userId + "::" + System.currentTimeMillis()).getBytes());
        return ResponseEntity.ok(Base64.getEncoder().encodeToString(encrypted));
    }
}
