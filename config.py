import re

ext = "kt"
category_re_dict = {
    "Production": re.compile(
        r"(?P<path>^[$]PROJECT_DIR[$][/](?P<module>.*)([/]src[/])(.*(kotlin|java))[/](?P<package>.*)[/](?P<name>.*)[.].*$)"),
    "Android": re.compile(
        r"(?P<path>.*[/]sdk[/].*[/](?P<module>android-[^\/]*)([/].*\.jar[!])*[/](?P<package>.*)[/](?P<name>.*)[.].*$)"),
    "ThirdParty": re.compile(
        r"(?P<path>.*[/].gradle[/]caches[/].*files-[^\/]*[/](?P<module>[^\/]*[/][^\/]*[/][^\/]*).*\.jar[!][/](?P<package>.*)[/](?P<name>.*)[.].*$)"),
    "LocalJar": re.compile(
        r"(?P<path>^[$]PROJECT_DIR[$][/](?P<module>.*)([/][^\/]*\.jar[!])[/](?P<package>.*)[/](?P<name>.*)[.].*$)"),
    "JDK": re.compile(
        r"(?P<path>^[$]PROJECT_DIR[$][/](?P<module>.*)([/][^\/]*\.jar[!])[/](?P<package>.*)[/](?P<name>.*)[.].*$)")
}
