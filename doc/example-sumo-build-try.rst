Example for sumo build try
==========================

.. _example-sumo-build-try:

Since the report of the "try" command is a bit complex, here is an example.

The output of "try" is in most cases very long, so you probably want to
redirect it to a file transfer it to a pager program like "less". You can skip
the detailed report with option "-b" or "--brief". In the following examples we
use "less". Note that in "less" you go back with "b", forward with <space> and
quit the program with "q". There are many other commands, use "man less" to
learn more. "less" is not available on windows platforms.

We assume that you have a configuration file "sumo-build.config" which contains
the settings for all needed command line options and a list of modules. Then we
start the program in our application directory like this::

  sumo-build try | less

In this example we see at the start of the output::

  Not all dependencies were included in module specifications, these modules
  have to be added:
      ALARM
      MISC_DBC

This means that the two mentioned modules are needed by other modules so we
have to add them to our module specifications. We add them on the command line
for now::
  
  sumo-build try ALARM MISC_DBC | less

At the start of the output we now see::

  Not all modules have exactly specified versions. These modules need an 
  exact version specification:
      ALARM
      MISC_DBC             -> suggested version: R3-0

The two modules need a version specification. For "MISC_DBC" the program has
found that you can only use one version, "R3-0" so we can use this. For "ALARM"
we have no further hints, so we have to investigate the rest of the report.
Further below you find::

  List of modules that fullfill the given module specification:

When we look for "ALARM" further below we find::

    "ALARM": {
        "R3-7": {
            "built": false,
            "dependents": {
                "MCAN:TAGLESS-2-6-3": "state: not tested"
            }
        },
        "R3-8": {
            "built": true,
            "dependents": {
                "MCAN:TAGLESS-2-6-3": "state: stable"
            }
        }
    },
  
We see that there are two versions of "ALARM", "R3-7" and "R3-8". Property "built" shows us, if the this version has been built with sumo, so we know that it can be compiled. "dependents" shows which other modules of our module specification list depend on "ALARM". In this case it is only "MCAN:TAGLESS-2-6-3". The "state" property shows what we know about this relation. These are possible values of the state:

state: no tested
  This means that there is no information if these modules are compatible,
  that they can be used together in a build or that they work.

state: scanned
  This means that these modules were used together in a support directory but
  only without sumo. 

state: testing
  This means that these modules have been used in a build and that the state of
  that build was marked "stable".

state: stable
  This means that these modules have been used in a build and that the state of
  that build was marked "stable".

If we look even further below for "ALARM" we find::

    "BASE": {
        "R3-14-12-2-1": {
            "built": true,
            "dependents": {
                "AGILENT-SUPPORT:R0-11": "state: stable",
                "AGILENT:R2-3": "state: stable",
                "ALARM:R3-7": "state: not tested",
                "ALARM:R3-8": "state: stable",
                "APPS_GENERICBOOT:R0-8-3": "state: stable",
                "APPS_GENERICTEMPLATE:R3-7": "state: stable",
                "APPS_IOCWATCH:R3-1": "state: stable",
                ...
            }
        }
    }

This means that "ALARM:R3-7" and "ALARM:R3-8" depend on "BASE:R3-14-12-2-1". We
see only this version of "BASE" here since we have specified exactly this
version of base in our module specifications. We see that "ALARM:R3-8" was in a
build with "BASE:R3-14-12-2-1" and that this build was marked "stable".

So we decide the use "ALARM:R3-8" and "MISC_DBC:R3-0". We use command "try"
again::

  sumo-build try ALARM:R3-8 MISC_DBC:R3-0 | less

Now we see at the start of the output::

  The following modules are not needed by other modules in your module
  specification:
      AGILENT
      AGILENT-SUPPORT
      ...

This is an overview of modules that are not needed by other modules in your
module specifications. You may use this to remove modules that your application
doesn't need, in this case you would remove them in your configuration file.

We see at the end of the output::

  Command 'new' would create build with tag 'AUTO-001'
  
  Your module specifications are complete. You can use these with command
  'new' to create a new build.

This means that our module specification would now work with command "new". We
add "ALARM:R3-8" and "MISC_DBC:R3-0" to the file sumo-build.config at key
"module" and can then create a build with::

  sumo-build new


