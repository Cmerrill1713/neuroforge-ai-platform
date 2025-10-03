# 🚨 CURSOR WORK REQUIREMENTS - MANDATORY

**⚠️ CRITICAL**: This file MUST be read before any Cursor work can proceed.

---

## 🚫 **WORK IS BLOCKED UNTIL REQUIREMENTS ARE MET**

### **MANDATORY PRE-WORK CHECKLIST**

Before ANY work can be done, you MUST complete ALL of the following:

#### 1. **READ REQUIRED DOCUMENTATION** (MANDATORY)
- ✅ `SYSTEM_OVERVIEW_MASTER.md` - Start here
- ✅ `SYSTEM_ARCHITECTURE_MAP.md` - Architecture details
- ✅ `FEATURE_DEPENDENCY_MAP.md` - Feature dependencies  
- ✅ `CURSOR_WORK_REQUIREMENTS.md` - Development requirements

#### 2. **RUN SYSTEM VALIDATION** (MANDATORY)
```bash
python3 MANDATORY_SYSTEM_VALIDATOR.py
```
**Must return exit code 0 (success)**

#### 3. **RUN PREFLIGHT CHECK** (MANDATORY)
```bash
python3 CURSOR_MANDATORY_PREFLIGHT.py
```
**Must return exit code 0 (success)**

#### 4. **CHECK SYSTEM STATE** (MANDATORY)
```bash
python3 system_cli.py
```
**Must show all services as "up"**

#### 5. **VERIFY PORT AVAILABILITY** (MANDATORY)
```bash
lsof -i :8004  # Backend (must be available)
lsof -i :3000  # Frontend (must be available)
lsof -i :11434 # Ollama (must be available)
```

---

## 🔧 **ENFORCEMENT MECHANISMS**

### **Automatic Enforcement**
The system automatically enforces these requirements through:

1. **`.cursorrules`** - Cursor IDE rules
2. **`MANDATORY_SYSTEM_VALIDATOR.py`** - System validation
3. **`CURSOR_MANDATORY_PREFLIGHT.py`** - Preflight checks
4. **`ENFORCE_CURSOR_RULES.py`** - Rule enforcement

### **Blocking Behavior**
If requirements are not met:
- ❌ Work is BLOCKED
- ❌ Scripts return exit code 1
- ❌ Error messages explain what's required
- ❌ Must fix issues before proceeding

---

## 📋 **STEP-BY-STEP WORKFLOW**

### **Step 1: Read Documentation**
```bash
# Read these files in order:
cat SYSTEM_OVERVIEW_MASTER.md
cat SYSTEM_ARCHITECTURE_MAP.md
cat FEATURE_DEPENDENCY_MAP.md
cat CURSOR_WORK_REQUIREMENTS.md
```

### **Step 2: Run Validation**
```bash
# Run system validation
python3 MANDATORY_SYSTEM_VALIDATOR.py

# Check exit code (must be 0)
echo $?
```

### **Step 3: Run Preflight**
```bash
# Run preflight check
python3 CURSOR_MANDATORY_PREFLIGHT.py

# Check exit code (must be 0)
echo $?
```

### **Step 4: Check System State**
```bash
# Check system state
python3 system_cli.py

# Verify all services are "up"
```

### **Step 5: Verify Ports**
```bash
# Check port availability
lsof -i :8004  # Should be available
lsof -i :3000  # Should be available
lsof -i :11434 # Should be available
```

### **Step 6: Start Work**
Only after ALL checks pass can work begin.

---

## 🚨 **COMMON BLOCKING ISSUES**

### **Documentation Not Read**
```
❌ BLOCKING: Required documentation not read recently
📖 REQUIRED: Read all documentation before proceeding
```
**Solution**: Read all required documentation files

### **System Validation Failed**
```
❌ BLOCKING: System validation failed
🔧 REQUIRED: Fix system issues before proceeding
```
**Solution**: Run `python3 MANDATORY_SYSTEM_VALIDATOR.py` and fix issues

### **Preflight Check Failed**
```
❌ BLOCKING: Preflight check failed
🔧 REQUIRED: Run preflight check before proceeding
```
**Solution**: Run `python3 CURSOR_MANDATORY_PREFLIGHT.py` and fix issues

### **Port Conflicts**
```
❌ BLOCKING: Required port 8004 is in use
🔧 REQUIRED: Free up port before proceeding
```
**Solution**: Kill processes using required ports

---

## 🎯 **SUCCESS INDICATORS**

### **All Requirements Met When:**
- ✅ All documentation files exist and are recent
- ✅ System validation returns exit code 0
- ✅ Preflight check returns exit code 0
- ✅ System CLI shows all services as "up"
- ✅ Required ports are available
- ✅ No blocking errors in logs

### **Work Can Proceed When:**
- ✅ All enforcement checks pass
- ✅ System is in healthy state
- ✅ Dependencies are met
- ✅ Documentation is current

---

## 🔧 **TROUBLESHOOTING**

### **If Validation Fails**
1. Check the error message
2. Fix the identified issue
3. Re-run validation
4. Repeat until success

### **If Preflight Fails**
1. Ensure documentation is read
2. Ensure system validation passed
3. Re-run preflight check
4. Repeat until success

### **If System State is Bad**
1. Check logs for errors
2. Restart required services
3. Verify dependencies
4. Re-run system check

---

## 📞 **GETTING HELP**

### **Self-Help Resources**
1. **Documentation**: Read all required docs
2. **Validation Scripts**: Run and fix issues
3. **System CLI**: Check system state
4. **Logs**: Check for error messages

### **Emergency Procedures**
1. **System Down**: Restart services
2. **Port Conflicts**: Kill conflicting processes
3. **Dependency Issues**: Reinstall dependencies
4. **Validation Errors**: Fix identified issues

---

## ⚠️ **IMPORTANT NOTES**

### **These Rules Are:**
- 🚫 **NON-NEGOTIABLE**
- 🚫 **ENFORCED AUTOMATICALLY**
- 🚫 **CANNOT BE BYPASSED**
- 🚫 **REQUIRED FOR ALL WORK**

### **Violation Consequences:**
- ❌ Work is blocked
- ❌ Scripts fail with exit code 1
- ❌ Must fix issues before proceeding
- ❌ No exceptions allowed

---

**🎯 REMEMBER**: These requirements exist to prevent recurring issues and ensure system stability. Follow them exactly or work will be blocked.

---

**Last Updated**: January 2025  
**Status**: 🚫 **ENFORCED**  
**Compliance**: **MANDATORY**
