package output

import (
	"encoding/json"
)

type EventType string

const (
	EventTypeVersion           EventType = "Version"
	EventTypeInfo                        = "Info"
	EventTypeId                          = "Id"
	EventTypeInitialTime                 = "InitialTime"
	EventTypeLog                         = "Log"
	EventTypeLogHtml                     = "LogHtml"
	EventTypeStartRun                    = "StartRun"
	EventTypeEndRun                      = "EndRun"
	EventTypeStartTask                   = "StartTask"
	EventTypeEndTask                     = "EndTask"
	EventTypeStartElement                = "StartElement"
	EventTypeEndElement                  = "EndElement"
	EventTypeElementArgument             = "ElementArgument"
	EventTypeAssignElement               = "AssignElement"
	EventTypeTag                         = "Tag"
	EventTypeStartTime                   = "StartTime"
	EventTypeStartTraceback              = "StartTraceback"
	EventTypeTracebackEntry              = "TracebackEntry"
	EventTypeTracebackVariable           = "TracebackVariable"
	EventTypeEndTraceback                = "EndTraceback"
	EventTypeUnknown                     = "Unknown"
)

type Event struct {
	Type   EventType              `json:"message_type"`
	Fields map[string]interface{} `json:"-"`
}

type Events struct {
	events []Event
}

func New() Events {
	return Events{
		events: make([]Event, 0),
	}
}

func (e *Events) Parse(line string) {
	var event Event
	if err := json.Unmarshal([]byte(line), &event.Fields); err != nil {
		return
	}

	eventType, ok := event.Fields["message_type"].(string)
	if !ok {
		return
	}

	event.Type = TypeFromString(eventType)
	delete(event.Fields, "message_type")

	e.events = append(e.events, event)
}

func TypeFromString(value string) EventType {
	switch value {
	case "V":
		return EventTypeVersion
	case "I":
		return EventTypeInfo
	case "ID":
		return EventTypeId
	case "T":
		return EventTypeInitialTime
	case "L":
		return EventTypeLog
	case "LH":
		return EventTypeLogHtml
	case "SR":
		return EventTypeStartRun
	case "ER":
		return EventTypeEndRun
	case "ST":
		return EventTypeStartTask
	case "ET":
		return EventTypeEndTask
	case "SE":
		return EventTypeStartElement
	case "EE":
		return EventTypeEndElement
	case "EA":
		return EventTypeElementArgument
	case "AS":
		return EventTypeAssignElement
	case "TG":
		return EventTypeTag
	case "S":
		return EventTypeStartTime
	case "STB":
		return EventTypeStartTraceback
	case "TBE":
		return EventTypeTracebackEntry
	case "TBV":
		return EventTypeTracebackVariable
	case "ETB":
		return EventTypeEndTraceback
	default:
		return EventTypeUnknown
	}
}
