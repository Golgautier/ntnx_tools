package main

import (
	"fmt"
	"ntnx_api_call/ntnx_api_call"
	"os"
)

func main() {
	// Variable definitions
	var myEndpoint ntnx_api_call.Ntnx_endpoint
	var StoContainerList = make(map[string]string)
	var outputfile string = "./output.csv"

	// Deactivate SSL Check
	ActivateSSLCheck(false)

	// Get Prism info from user
	GetEnpointInformation(&myEndpoint)

	// Get Storage Container List

	fmt.Println(symbols["INFO"], " Getting Storage Container list...")
	type StructTmp struct {
		Entities []struct {
			StorageContainerUUID string `json:"storage_container_uuid"`
			Name                 string `json:"name"`
		} `json:"entities"`
	}

	var SCList StructTmp

	myEndpoint.CallAPIJSON("PE", "GET", "/PrismGateway/services/rest/v2.0/storage_containers", "", &SCList)

	// Parse all SC
	for tmp := range SCList.Entities {
		StoContainerList[SCList.Entities[tmp].StorageContainerUUID] = SCList.Entities[tmp].Name
	}

	fmt.Println(symbols["OK"], " Ok")

	// Get VG list

	fmt.Println(symbols["INFO"], " VG Analysis...")

	type StructTmp2 struct {
		Entities []struct {
			UUID        string `json:"uuid"`
			Name        string `json:"name"`
			Description string `json:"description,omitempty"`
			DiskList    []struct {
				StorageContainerUUID string `json:"storage_container_uuid"`
			} `json:"disk_list"`
		} `json:"entities"`
	}

	var VGList StructTmp2

	myEndpoint.CallAPIJSON("PE", "GET", "/PrismGateway/services/rest/v2.0/volume_groups", "", &VGList)

	f, err := os.Create(outputfile)
	CheckErr("Creation of"+outputfile, err)
	f.WriteString("UUID;Name;Container;Description\n")

	defer f.Close()

	count := 0
	// Parse all VG an put them in a file
	for tmp := range VGList.Entities {
		_, err2 := f.WriteString(VGList.Entities[tmp].UUID + ";" + VGList.Entities[tmp].Name + ";" + StoContainerList[VGList.Entities[tmp].DiskList[0].StorageContainerUUID] + ";" + VGList.Entities[tmp].Description + "\n")
		CheckErr("Writing in output file", err2)
		count++
	}

	fmt.Println(symbols["OK"], " Output file "+outputfile+" finished. Contains "+fmt.Sprint(count)+" VG.")

}
