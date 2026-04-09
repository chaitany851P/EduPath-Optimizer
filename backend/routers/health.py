"""
Health Check & Monitoring Module for EduPath Optimizer
Provides comprehensive system health diagnostics for production deployments
"""

from datetime import datetime
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncDatabase
from backend.config import settings
import psutil
import platform

router = APIRouter(prefix="/api/health", tags=["Health & Monitoring"])


class HealthStatus:
    """Health check status markers"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


async def check_database_health(db: AsyncDatabase) -> Dict:
    """Check MongoDB connection and collections"""
    try:
        # Test connection
        await db.command('ping')
        
        # Check collections
        collections = await db.list_collection_names()
        required = ['students', 'subjects', 'attendance', 'academic_performance']
        missing = [c for c in required if c not in collections]
        
        status = HealthStatus.HEALTHY if not missing else HealthStatus.DEGRADED
        
        return {
            'status': status,
            'database': settings.MONGODB_DATABASE,
            'collections': {
                'total': len(collections),
                'required_count': len(required),
                'missing': missing,
            },
            'connected': True,
        }
    except Exception as e:
        return {
            'status': HealthStatus.UNHEALTHY,
            'error': str(e),
            'connected': False,
        }


def check_system_resources() -> Dict:
    """Check CPU, memory, and disk usage"""
    return {
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory': {
            'percent': psutil.virtual_memory().percent,
            'available_gb': round(psutil.virtual_memory().available / (1024**3), 2),
        },
        'disk': {
            'percent': psutil.disk_usage('/').percent,
            'free_gb': round(psutil.disk_usage('/').free / (1024**3), 2),
        },
    }


def check_system_info() -> Dict:
    """Get system information"""
    return {
        'platform': platform.system(),
        'platform_version': platform.platform(),
        'python_version': platform.python_version(),
        'hostname': platform.node(),
    }


async def get_database_stats(db: AsyncDatabase) -> Dict:
    """Get collection statistics"""
    try:
        stats = {}
        for collection in ['students', 'subjects', 'attendance', 'academic_performance', 'campuses', 'departments']:
            count = await db[collection].count_documents({})
            stats[collection] = count
        return stats
    except:
        return {}


@router.get("/ping")
async def ping():
    """Simple ping endpoint for uptime checks"""
    return {
        "status": "pong",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/live")
async def liveness_probe():
    """Kubernetes/Docker liveness probe"""
    return {
        "status": "alive",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@router.get("/ready")
async def readiness_probe(db: AsyncDatabase):
    """Kubernetes/Docker readiness probe - checks if system is ready to handle traffic"""
    db_health = await check_database_health(db)
    
    if db_health.get('status') != HealthStatus.HEALTHY:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "reason": "Database not ready",
                "database": db_health
            }
        )
    
    return {
        "status": "ready",
        "database": "connected",
    }


@router.get("/full")
async def full_health_check(db: AsyncDatabase):
    """Comprehensive health check with all diagnostics"""
    db_health = await check_database_health(db)
    system_resources = check_system_resources()
    system_info = check_system_info()
    db_stats = await get_database_stats(db)
    
    # Determine overall status
    overall_status = HealthStatus.HEALTHY
    if db_health.get('status') == HealthStatus.UNHEALTHY:
        overall_status = HealthStatus.UNHEALTHY
    elif (system_resources['cpu_percent'] > 90 or 
          system_resources['memory']['percent'] > 90):
        overall_status = HealthStatus.DEGRADED
    
    return {
        'status': overall_status,
        'timestamp': datetime.utcnow().isoformat(),
        'app': {
            'name': settings.APP_NAME,
            'version': settings.APP_VERSION,
            'environment': settings.ENVIRONMENT,
        },
        'university': {
            'name': settings.UNIVERSITY_NAME,
            'multi_campus': settings.ENABLE_MULTI_CAMPUS,
            'multi_department': settings.ENABLE_MULTI_DEPARTMENT,
        },
        'database': db_health,
        'resources': system_resources,
        'system': system_info,
        'collections_stats': db_stats,
        'features': {
            'phase_1': settings.ENABLE_PHASE_1,
            'phase_2': settings.ENABLE_PHASE_2,
            'phase_3': settings.ENABLE_PHASE_3,
            'email_notifications': settings.ENABLE_EMAIL_NOTIFICATIONS,
        },
    }


@router.get("/metrics")
async def get_metrics(db: AsyncDatabase):
    """Get system metrics for monitoring dashboards"""
    db_health = await check_database_health(db)
    resources = check_system_resources()
    
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'uptime_seconds': int(__import__('time').time()),
        'database': {
            'connected': db_health.get('connected', False),
            'status': db_health.get('status'),
        },
        'resources': {
            'cpu_percent': resources['cpu_percent'],
            'memory_percent': resources['memory']['percent'],
            'memory_available_gb': resources['memory']['available_gb'],
            'disk_percent': resources['disk']['percent'],
            'disk_free_gb': resources['disk']['free_gb'],
        },
    }


@router.get("/capacity")
async def check_capacity(db: AsyncDatabase):
    """Check system capacity and scaling info"""
    system_resources = check_system_resources()
    
    # Determine capacity status
    cpu_status = "Normal" if system_resources['cpu_percent'] < 80 else "High" if system_resources['cpu_percent'] < 95 else "Critical"
    mem_status = "Normal" if system_resources['memory']['percent'] < 80 else "High" if system_resources['memory']['percent'] < 95 else "Critical"
    disk_status = "Normal" if system_resources['disk']['percent'] < 80 else "High" if system_resources['disk']['percent'] < 95 else "Critical"
    
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'cpu': {
            'usage_percent': system_resources['cpu_percent'],
            'status': cpu_status,
            'recommendation': 'Scale up if CPU reaches 95%' if system_resources['cpu_percent'] > 85 else 'Normal',
        },
        'memory': {
            'usage_percent': system_resources['memory']['percent'],
            'available_gb': system_resources['memory']['available_gb'],
            'status': mem_status,
            'recommendation': 'Increase memory if usage reaches 95%' if system_resources['memory']['percent'] > 85 else 'Normal',
        },
        'disk': {
            'usage_percent': system_resources['disk']['percent'],
            'free_gb': system_resources['disk']['free_gb'],
            'status': disk_status,
            'recommendation': 'Clean up storage if usage reaches 95%' if system_resources['disk']['percent'] > 85 else 'Normal',
        },
    }


@router.get("/status-page")
async def status_page(db: AsyncDatabase):
    """Public status page - minimal info for user-facing dashboard"""
    db_health = await check_database_health(db)
    
    service_status = "operational" if db_health.get('connected') else "degraded"
    
    return {
        'service': settings.APP_NAME,
        'status': service_status,
        'timestamp': datetime.utcnow().isoformat(),
        'components': {
            'api': 'operational',
            'database': 'operational' if db_health.get('connected') else 'investigating',
            'frontend': 'operational',
        },
    }
