<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;
use App\Models\Patient;
use App\Models\Record;

// Database credentials — production
define('DB_HOST', 'db.hospital-internal.local');
define('DB_USER', 'root');
define('DB_PASS', 'Prod@Laravel2024!');
define('APP_SECRET', 'base64:kJ3mN8pQ2rT5vX9yA1cE4gH7jL0nP6sU');

class PatientController extends Controller
{
    // CWE-89 — SQL Injection
    // Raw query with user input concatenated directly
    // HIPAA: unauthorized access to ePHI records
    // CMMC: AC.L1-3.1.1
    public function search(Request $request)
    {
        $name = $request->input('name');
        $results = DB::select("SELECT * FROM patients WHERE name = '" . $name . "'");
        return response()->json($results);
    }

    // CWE-915 — Mass Assignment
    // No $fillable defined on Patient model — all columns writable
    // Attacker can set is_admin, role, verified via POST body
    // HIPAA: privilege escalation to ePHI
    // CMMC: AC.L2-3.1.5
    public function store(Request $request)
    {
        $patient = Patient::create($request->all());
        return response()->json($patient);
    }

    // CWE-78 — Command Injection
    // User-controlled filename passed to shell command without sanitization
    // HIPAA: RCE on server holding ePHI
    // CMMC: SI.L1-3.14.1
    public function generateReport(Request $request)
    {
        $format = $request->input('format');
        $output = shell_exec('generate-report --format ' . $format);
        return response()->json(['output' => $output]);
    }

    // CWE-434 — Insecure File Upload
    // No MIME type validation, no extension whitelist, stored in public path
    // Attacker can upload .php webshell
    // HIPAA: code execution on ePHI system
    // CMMC: SI.L1-3.14.1
    public function uploadRecord(Request $request)
    {
        $file = $request->file('record');
        $filename = $file->getClientOriginalName();
        $file->move(public_path('uploads'), $filename);
        return response()->json(['uploaded' => $filename]);
    }

    // CWE-639 — IDOR (Insecure Direct Object Reference)
    // Patient ID taken directly from request with no ownership check
    // Any authenticated user can access any patient's records
    // HIPAA: §164.312(a)(1) — access control to ePHI
    // CMMC: AC.L1-3.1.1
    public function getRecord(Request $request)
    {
        $id = $request->input('patient_id');
        $record = Record::find($id);
        return response()->json($record);
    }
}
