package main

import (
	"crypto/tls"
	"fmt"
	"net/http"
	"ntnx_api_call/ntnx_api_call"
	"os"
	"strings"

	"golang.org/x/term"
	// "github.com/davecgh/go-spew/spew"
)

// Emoji symbols from http://www.unicode.org/emoji/charts/emoji-list.html
var symbols = map[string]string{
	"FAIL":    "\U0000274C",
	"INFO":    "\U0001F449",
	"OK":      "\U00002705",
	"WAIT":    "\U0001F55B",
	"NEUTRAL": "\U00002796",
	"START":   "\U0001F3C1",
	"WARN":    "\U00002757",
	"REFRESH": "\U00002755",
	"NOTICE":  "\U00002755",
}

// Color codes for terminal output
var colors = map[string]string{
	"GREEN":  "\033[32m",
	"ORANGE": "\033[33m",
	"RED":    "\033[31m",
	"BLUE":   "\033[36m",
	"END":    "\033[0m",
}

// =========== CheckErr ===========
// This function is will handle errors
func CheckErr(context string, err error) {
	if err != nil {
		fmt.Println(symbols["FAIL"], " ", context, " : ", err.Error())
		os.Exit(2)
	}
}

// =========== ActivateSSLCheck ===========
func ActivateSSLCheck(value bool) string {
	http.DefaultTransport.(*http.Transport).TLSClientConfig = &tls.Config{InsecureSkipVerify: !value}
	if value {
		return colors["GREEN"] + "activated" + colors["END"]
	} else {
		return colors["RED"] + "deactivated" + colors["END"]
	}
}

func GetEnpointInformation(Prism *ntnx_api_call.Ntnx_endpoint) {

	ok := false
	resp := ""

	for !ok {

		fmt.Print(symbols["NEUTRAL"], " Enter PE IP or FQDN : ")
		fmt.Scan(&Prism.PE)

		fmt.Print(symbols["NEUTRAL"], " Enter PE User : ")
		fmt.Scan(&Prism.User)

		fmt.Print(symbols["NEUTRAL"], " Enter PE password for ", Prism.User, ": ")
		tmppwd, err := term.ReadPassword(0)
		fmt.Println("")
		CheckErr("Get password", err)

		Prism.Password = string(tmppwd)

		Prism.Mode = "password"

		fmt.Print(symbols["NOTICE"], " Continue with these parameters (Y/N) ? ")
		fmt.Scan(&resp)

		if strings.ToUpper(resp) == "Y" {
			ok = true
		}
	}

}
