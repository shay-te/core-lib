module.exports.testInput = {
  "core_lib": {
    "name": "ExampleCoreLib",
    "env": {
      "USERDB_DB": "userdb",
      "USERDB_USER": "user",
      "USERDB_PASSWORD": "password",
      "USERDB_PORT": 5432,
      "USERDB_HOST": "localhost",
      "MONGODB_DB": "mongodb",
      "MONGODB_USER": "user",
      "MONGODB_PASSWORD": "password",
      "MONGODB_PORT": 27017,
      "MONGODB_HOST": "localhost",
      "REDISCACHE_PORT": 6379,
      "REDISCACHE_HOST": "localhost"
    },
    "connections": [
      {
        "key": "userdb",
        "migrate": true,
        "log_queries": false,
        "create_db": true,
        "session": {
          "pool_recycle": 3200,
          "pool_pre_ping": false
        },
        "url": {
          "file": "${oc.env:USERDB_DB}",
          "protocol": "postgresql",
          "username": "${oc.env:USERDB_USER}",
          "password": "${oc.env:USERDB_PASSWORD}",
          "port": "${oc.env:USERDB_PORT}",
          "host": "${oc.env:USERDB_HOST}"
        }
      },
      {
        "key": "sellerdb",
        "migrate": true,
        "log_queries": false,
        "create_db": true,
        "session": {
          "pool_recycle": 3200,
          "pool_pre_ping": false
        },
        "url": {
          "protocol": "sqlite"
        }
      },
      {
        "key": "mongodb",
        "migrate": false,
        "url": {
          "file": "${oc.env:MONGODB_DB}",
          "protocol": "mongodb",
          "username": "${oc.env:MONGODB_USER}",
          "password": "${oc.env:MONGODB_PASSWORD}",
          "port": "${oc.env:MONGODB_PORT}",
          "host": "${oc.env:MONGODB_HOST}"
        }
      }
    ],
    "caches": [
      {
        "key": "memorycache",
        "type": "memory"
      },
      {
        "key": "rediscache",
        "type": "redis",
        "url": {
          "host": "${oc.env:REDISCACHE_HOST}",
          "port": "${oc.env:REDISCACHE_PORT}",
          "protocol": "redis"
        }
      }
    ],
    "jobs": [
      {
        "key": "update_user",
        "initial_delay": "0s",
        "frequency": "",
        "handler": {
          "_target_": "example_core_lib.example_core_lib.jobs.update_user.UpdateUser"
        }
      }
    ],
    "entities": [
      {
        "key": "details",
        "db_connection": "userdb",
        "columns": [
          {
            "key": "username",
            "type": "VARCHAR",
            "default": "''",
            "nullable": true
          },
          {
            "key": "password",
            "type": "VARCHAR",
            "default": "''",
            "nullable": true
          },
          {
            "key": "active",
            "type": "BOOLEAN",
            "default": false,
            "nullable": true
          }
        ],
        "is_soft_delete": true,
        "is_soft_delete_token": true
      },
      {
        "key": "details",
        "db_connection": "sellerdb",
        "columns": [
          {
            "key": "username",
            "type": "VARCHAR",
            "default": "''",
            "nullable": false
          },
          {
            "key": "password",
            "type": "VARCHAR",
            "default": null,
            "nullable": true
          },
          {
            "key": "active",
            "type": "BOOLEAN",
            "default": false,
            "nullable": false
          }
        ],
        "is_soft_delete": true,
        "is_soft_delete_token": false
      },
      {
        "key": "data",
        "db_connection": "sellerdb",
        "columns": [
          {
            "key": "address",
            "type": "VARCHAR",
            "default": null,
            "nullable": true
          }
        ],
        "is_soft_delete": false,
        "is_soft_delete_token": false
      },
      {
        "key": "post_data",
        "db_connection": "mongodb",
        "columns": [],
        "is_soft_delete": false,
        "is_soft_delete_token": false
      }
    ],
    "data_accesses": [
      {
        "key": "DetailsDataAccess",
        "entity": "details",
        "db_connection": "userdb",
        "is_crud": true,
        "is_crud_soft_delete": true,
        "is_crud_soft_delete_token": true
      },
      {
        "key": "SellerDetailsDataAccess",
        "entity": "details",
        "db_connection": "sellerdb",
        "is_crud": true,
        "is_crud_soft_delete": true
      },
      {
        "key": "DataDataAccess",
        "entity": "data",
        "db_connection": "sellerdb"
      },
      {
        "key": "PostDataDataAccess",
        "entity": "post_data",
        "db_connection": "mongodb"
      }
    ],
    "setup": {
      "author": "nam",
      "author_email": "name@name.com",
      "description": "Project",
      "url": "",
      "license": "MIT",
      "classifiers": [
        "Development Status :: 3 - Alpha",
        "Development Status :: 4 - Beta",
        "Development Status :: 5 - Production/Stable",
        "Environment :: MacOS X",
        "Environment :: Win32 (MS Windows)",
        "Framework :: Django :: 4.0"
      ],
      "version": "0.0.0.1"
    }
  }
}
